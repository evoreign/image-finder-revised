import express, { Request, Response, NextFunction } from 'express';
import mongoose from 'mongoose';
import helmet from 'helmet';
import cache from 'memory-cache';

const router = express.Router();

router.use(helmet()); // Use Helmet for basic security

router.use((req: Request, res: Response, next: NextFunction) => {
  next();
});

router.get('/', (req: Request, res: Response) => {
  res.send('Search home page');
});

const getImageId = (req: Request): string => {
  const imageId = String(req.params.ImageId);

  if (!Number.isInteger(Number(imageId)) || Number(imageId) < 0) {
    throw new Error('Invalid ImageId');
  }

  return imageId;
};

const getModelsFromDb = async (imageId: string) => {
  console.log(`Searching for image ID: ${imageId}`);
  console.log(`Current database: ${mongoose.connection.db.databaseName}`);
  const models = await mongoose.connection.db.collection('models')
    .find({ [`PsType.${imageId}`]: { $exists: true } })
    .toArray();
  console.log(`Found ${models.length} models`);

  return models;
};

const formatResults = (models: any[], imageId: string) => {
  const results = models.map(model => ({
    Brand: model.Brand,
    ModelName: model.ModelName,
    ImageUrl: model.ImageUrl,
    PsType: model.PsType[imageId]
  }));
  console.log(`Results: ${JSON.stringify(results)}`);

  return results;
};

router.get('/all', async (req: Request, res: Response) => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const skip = (page - 1) * limit;
    const brand = req.query.brand as string;
    const pstype = req.query.pstype as string;

    const cacheKey = `allModels-page:${page}-limit:${limit}-brand:${brand}-pstype:${pstype}`;
    const cacheValue = cache.get(cacheKey);
    if (cacheValue) {
      return res.json(cacheValue);
    }

    // Build the query object based on the provided parameters
    const query: any = {};
    if (brand) query.Brand = brand;
    if (pstype) query[`PsType.${pstype}`] = { $exists: true };

    // Fetch all documents from the database
    const models = await mongoose.connection.db.collection('models')
      .find(query)
      .skip(skip)
      .limit(limit)
      .toArray();

    // Get the total number of models
    const totalModels = await mongoose.connection.db.collection('models').countDocuments(query);

    // Calculate the total number of pages
    const totalPages = Math.ceil(totalModels / limit);

    // Map over the documents and only return the model, ImageUrl fields and keys of data
    const results = models
      .filter(model => !pstype || model.PsType[pstype])
      .map(model => ({
        Brand: model.Brand,
        ModelName: model.ModelName,
        ImageUrl: model.ImageUrl,
        PsType: pstype ? model.PsType[pstype] : model.PsType
      }));

    const response = { results, totalPages };

    cache.put(cacheKey, response, 600000); // Cache for 10 minute

    // Send the results back to the client
    res.json(response);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

router.get('/:ImageId', async (req: Request, res: Response) => { 
  try {
    const imageId = getImageId(req);

    const cacheKey = `ImageId:${imageId}`;
    const cacheValue = cache.get(cacheKey);
    if (cacheValue) {
      return res.json(cacheValue);
    }

    const models = await getModelsFromDb(imageId);
    const results = formatResults(models, imageId);

    cache.put(cacheKey, results, 600000); // Cache for 10 minute

    res.json(results);
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: error.message });
  }
});

export default router;