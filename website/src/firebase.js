// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFunctions } from "firebase/functions";
import { getDatabase } from "firebase/database";

// Lazy load Firebase Analytics library
/**
 * @type {import("@firebase/analytics").Analytics}
 */
let analytics;

async function getAnalytics() {
  if (!analytics) {
    const { getAnalytics } = await import('firebase/analytics');
    analytics = getAnalytics(app);
  }
  return analytics;
}

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries
// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyBa7WNFwugtTqRwm8hqMsMgeExmRX_tEpw",
    authDomain: "just-another-future.firebaseapp.com",
    databaseURL: 'https://just-another-future-default-rtdb.asia-southeast1.firebasedatabase.app',
    projectId: "just-another-future",
    storageBucket: "just-another-future.appspot.com",
    messagingSenderId: "1001702454477",
    appId: "1:1001702454477:web:8068c9f2f39ded3bb76584",
    measurementId: "G-XEE5RNJMHF"
};
// Initialize Firebase
const app = initializeApp(firebaseConfig);
const functions = getFunctions(app);
const database = getDatabase(app);
export { app, getAnalytics, functions, database };
