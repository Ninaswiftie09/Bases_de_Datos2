const createCrudRouter = require("./createCrudRouter");
const reviewController = require("../controllers/reviewController");

module.exports = createCrudRouter(reviewController);