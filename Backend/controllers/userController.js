const createCrudController = require("./crudFactory");
const User = require("../models/User");

const crud = createCrudController(User);

exports.getAll = crud.getAll;
exports.getOne = crud.getOne;
exports.createOne = crud.createOne;
exports.updateOne = crud.updateOne;
exports.deleteOne = crud.deleteOne;

// ARRAYS
//  Se implementó manejo de arrays embebidos en usuarios, para agregar y eliminar
// direcciones con $push y $pull

exports.addAddress = async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { $push: { addresses: req.body } },
      { new: true }
    );
    res.json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

exports.removeAddress = async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { $pull: { addresses: { label: req.body.label } } },
      { new: true }
    );

    res.json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};