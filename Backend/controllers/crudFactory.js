const mongoose = require("mongoose");

function isValidObjectId(id) {
  return mongoose.Types.ObjectId.isValid(id);
}

function createCrudController(Model) {
  return {
    createOne: async (req, res) => {
      try {
        const created = await Model.create(req.body);
        res.status(201).json(created);
      } catch (error) {
        res.status(400).json({
          message: "Error al crear documento",
          error: error.message,
        });
      }
    },

    createMany: async (req, res) => {
      try {
        const docs = req.body;

        if (!Array.isArray(docs) || docs.length === 0) {
          return res.status(400).json({
            message: "Debés enviar un arreglo con al menos un documento",
          });
        }

        const created = await Model.insertMany(docs, { ordered: false });
        res.status(201).json({
          message: "Documentos creados correctamente",
          insertedCount: created.length,
          data: created,
        });
      } catch (error) {
        res.status(400).json({
          message: "Error al crear varios documentos",
          error: error.message,
        });
      }
    },

    getAll: async (req, res) => {
      try {
        const page = parseInt(req.query.page, 10) || 1;
        const limit = Math.min(parseInt(req.query.limit, 10) || 50, 200);
        const skip = (page - 1) * limit;

        const sortBy = req.query.sortBy || "created_at";
        const order = req.query.order === "asc" ? 1 : -1;

        const data = await Model.find({})
          .sort({ [sortBy]: order })
          .skip(skip)
          .limit(limit);

        const total = await Model.countDocuments();

        res.json({
          total,
          page,
          limit,
          data,
        });
      } catch (error) {
        res.status(500).json({
          message: "Error al obtener documentos",
          error: error.message,
        });
      }
    },

    getOne: async (req, res) => {
      try {
        const { id } = req.params;

        if (!isValidObjectId(id)) {
          return res.status(400).json({ message: "ID inválido" });
        }

        const doc = await Model.findById(id);

        if (!doc) {
          return res.status(404).json({ message: "Documento no encontrado" });
        }

        res.json(doc);
      } catch (error) {
        res.status(500).json({
          message: "Error al obtener documento",
          error: error.message,
        });
      }
    },

    updateOne: async (req, res) => {
      try {
        const { id } = req.params;

        if (!isValidObjectId(id)) {
          return res.status(400).json({ message: "ID inválido" });
        }

        const updated = await Model.findByIdAndUpdate(id, req.body, {
          new: true,
          runValidators: true,
        });

        if (!updated) {
          return res.status(404).json({ message: "Documento no encontrado" });
        }

        res.json(updated);
      } catch (error) {
        res.status(400).json({
          message: "Error al actualizar documento",
          error: error.message,
        });
      }
    },

    updateMany: async (req, res) => {
      try {
        const { ids, update } = req.body;

        if (!Array.isArray(ids) || ids.length === 0) {
          return res.status(400).json({
            message: "Debés enviar un arreglo de ids",
          });
        }

        if (!update || typeof update !== "object") {
          return res.status(400).json({
            message: "Debés enviar el objeto update",
          });
        }

        const invalidId = ids.find((id) => !isValidObjectId(id));
        if (invalidId) {
          return res.status(400).json({
            message: `ID inválido encontrado: ${invalidId}`,
          });
        }

        const result = await Model.updateMany(
          { _id: { $in: ids } },
          { $set: update },
          { runValidators: true }
        );

        res.json({
          message: "Documentos actualizados correctamente",
          matchedCount: result.matchedCount,
          modifiedCount: result.modifiedCount,
        });
      } catch (error) {
        res.status(400).json({
          message: "Error al actualizar varios documentos",
          error: error.message,
        });
      }
    },

    deleteOne: async (req, res) => {
      try {
        const { id } = req.params;

        if (!isValidObjectId(id)) {
          return res.status(400).json({ message: "ID inválido" });
        }

        const deleted = await Model.findByIdAndDelete(id);

        if (!deleted) {
          return res.status(404).json({ message: "Documento no encontrado" });
        }

        res.json({ message: "Documento eliminado correctamente" });
      } catch (error) {
        res.status(500).json({
          message: "Error al eliminar documento",
          error: error.message,
        });
      }
    },

    deleteMany: async (req, res) => {
      try {
        const { ids } = req.body;

        if (!Array.isArray(ids) || ids.length === 0) {
          return res.status(400).json({
            message: "Debés enviar un arreglo de ids",
          });
        }

        const invalidId = ids.find((id) => !isValidObjectId(id));
        if (invalidId) {
          return res.status(400).json({
            message: `ID inválido encontrado: ${invalidId}`,
          });
        }

        const result = await Model.deleteMany({ _id: { $in: ids } });

        res.json({
          message: "Documentos eliminados correctamente",
          deletedCount: result.deletedCount,
        });
      } catch (error) {
        res.status(500).json({
          message: "Error al eliminar varios documentos",
          error: error.message,
        });
      }
    },
  };
}

module.exports = createCrudController;