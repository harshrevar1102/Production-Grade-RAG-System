const express = require("express");

const {
  register,
  login,
  getMe,
  forgotPassword,
  resetPassword,
  changePassword,
} = require("../controllers/auth.controller");

const authenticate = require("../middleware/auth.middleware");

const router = express.Router();


// REGISTER
router.post("/register", register);


// LOGIN
router.post("/login", login);


// CURRENT USER
router.get("/me", authenticate, getMe);


// FORGOT PASSWORD
router.post("/forgot-password", forgotPassword);


// RESET PASSWORD
router.post("/reset-password", resetPassword);


// CHANGE PASSWORD
router.post(
  "/change-password",
  authenticate,
  changePassword
);


module.exports = router;