const mongoose = require("mongoose");
const { GridFSBucket } = require("mongodb");
const multer = require("multer");

const storage = multer.memoryStorage();
exports.upload = multer({ storage });

let bucket;

mongoose.connection.once("open", () => {
  bucket = new GridFSBucket(mongoose.connection.db, {
    bucketName: "uploads"
  });
});

// El sistema permite...

// Subir

exports.uploadFile = async (req, res) => {
  try {
    const uploadStream = bucket.openUploadStream(req.file.originalname);
    uploadStream.end(req.file.buffer);

    res.status(201).json({ message: "Archivo subido" });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

// Listar

exports.getFiles = async (req, res) => {
  const files = await bucket.find().toArray();
  res.json(files);
};

// Descargar

exports.downloadFile = async (req, res) => {
  bucket.openDownloadStreamByName(req.params.filename)
    .pipe(res);
};

// Y Eliminar Archivos

exports.deleteFile = async (req, res) => {
  await bucket.delete(new mongoose.Types.ObjectId(req.params.id));
  res.json({ message: "Archivo eliminado" });
};