const express = require("express");
const morgan = require("morgan");

const authRoutes = require("./routes/auth.routes");

const app = express();

// ==========================================
// MIDDLEWARE
// ==========================================

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan("dev"));

// ==========================================
// ROUTES
// ==========================================

app.get("/", (req, res) => {
  res.json({
    message: "Welcome to PRODUCTION-GRADE-RAG-SYSTEM",
  });
});

app.use("/api/auth", authRoutes);

// ==========================================
// ERROR HANDLER
// ==========================================

app.use((err, req, res, next) => {
  console.error(err);

  const statusCode = err.statusCode || 500;

  res.status(statusCode).json({
    success: false,
    message: err.message || "Internal server error",
  });
});

module.exports = app;