import express from 'express';
const SearchRouter = express.Router();

SearchRouter.get('/:slug', (req, res) => {
  const { slug } = req.params;
  // Do something with the slug
  res.send(`Search: ${slug}`);
});

export default SearchRouter;