const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const morgan = require("morgan");

dotenv.config();

const app = express();

app.use(cors());

app.use(express.json());

app.use(morgan("dev"));

app.get("/", (req, res) => {
    res.json({
        message: "Welcome to PRODUCTION-GRADE-RAG-SYSTEM",
    });
});

module.exports = app;