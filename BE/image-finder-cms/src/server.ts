import { config as dotenvConfig } from 'dotenv';
import express from 'express'
import payload from 'payload'
import { mediaManagement } from "payload-cloudinary-plugin";
import SearchRouter from './routes/search/search';
dotenvConfig();
const app = express()

const cloudinaryConfig = {
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
};

app.use(mediaManagement(cloudinaryConfig));

// Redirect root to Admin panel
app.get('/', (_, res) => {
  res.redirect('/admin')
})

const start = async () => {
  // Initialize Payload
  await payload.init({
    secret: process.env.PAYLOAD_SECRET,
    express: app,
    onInit: async () => {
      payload.logger.info(`Payload Admin URL: ${payload.getAdminURL()}`)
    },
  })

  // Add your own express routes here
  app.get('/hello', (_, res) => {
    res.send('Hello, world');
  });
  app.use('/search', SearchRouter);
  app.listen(4000)
}

start()