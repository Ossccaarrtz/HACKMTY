import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, onAuthStateChanged, createUserWithEmailAndPassword,
  signInWithEmailAndPassword, signOut, updateProfile
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, doc, setDoc, getDoc, serverTimestamp
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import {
  getStorage, ref, uploadBytes, getDownloadURL
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-storage.js";

// ⚠️ Sustituye por tus credenciales Firebase
const firebaseConfig = {
  apiKey: "AIzaSyBigSi_OAKkQkS81gjKkeqVyyW9gA93RJY",
  authDomain: "studio-7498188229-3d063.firebaseapp.com",
  projectId: "studio-7498188229-3d063",
  storageBucket: "studio-7498188229-3d063.firebasestorage.app",
  messagingSenderId: "243541606263",
  appId: "1:243541606263:web:9bbbe8726e5cadb0bfeb72"
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export {
  onAuthStateChanged, createUserWithEmailAndPassword, signInWithEmailAndPassword,
  signOut, updateProfile, doc, setDoc, getDoc, serverTimestamp,
  ref, uploadBytes, getDownloadURL
};
