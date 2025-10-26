import {
  auth,
  db,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  updateProfile,
  doc,
  setDoc,
  serverTimestamp,
} from "./firebaseConfig.js";

import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const $ = (id) => document.getElementById(id);
const show = (el) => el.classList.remove("hidden");
const hide = (el) => el.classList.add("hidden");

//  1. Siempre cerrar sesión al cargar login.html
signOut(auth)
  .then(() => console.log("Sesión cerrada al entrar a login.html"))
  .catch((err) => console.error("Error al cerrar sesión:", err));

// Cambiar entre registro y login
$("goLogin").onclick = () => {
  hide($("registerForm"));
  show($("loginForm"));
};
$("goRegister").onclick = () => {
  hide($("loginForm"));
  show($("registerForm"));
};

//  2. Registrar usuario con email
$("btnRegister").onclick = async () => {
  const nombre = $("regNombre").value.trim();
  const empresa = $("regEmpresa").value.trim();
  const giro = $("regGiro").value;
  const email = $("regEmail").value.trim();
  const pass = $("regPass").value.trim();
  const regMsg = $("regMsg");

  if (!nombre || !empresa || !giro || !email || !pass)
    return (regMsg.textContent = "Completa todos los campos.");

  try {
    regMsg.textContent = "Creando cuenta...";
    const cred = await createUserWithEmailAndPassword(auth, email, pass);
    await updateProfile(cred.user, { displayName: nombre });

    await setDoc(doc(db, "users", cred.user.uid), {
      id: cred.user.uid, // ⚠️ este campo es obligatorio por tus reglas
      nombre,
      empresa,
      giro,
      email,
      fechaRegistro: serverTimestamp(),
    });

    regMsg.textContent = "Cuenta creada correctamente. Redirigiendo...";
    setTimeout(() => (window.location.href = "index.html"), 1000);
  } catch (err) {
    regMsg.textContent = "Error: " + err.message;
  }
};

//  3. Iniciar sesión con email
$("btnLogin").onclick = async () => {
  const email = $("logEmail").value.trim();
  const pass = $("logPass").value.trim();
  const logMsg = $("logMsg");

  try {
    logMsg.textContent = "Iniciando sesión...";
    await signInWithEmailAndPassword(auth, email, pass);
    logMsg.textContent = "Bienvenido.";
    setTimeout(() => (window.location.href = "index.html"), 1000);
  } catch (err) {
    logMsg.textContent = "Error: " + err.message;
  }
};

//  4. Iniciar sesión con Google solo al hacer clic
const provider = new GoogleAuthProvider();
provider.setCustomParameters({
  prompt: "select_account",
});

const handleGoogleSignIn = async () => {
  try {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;

    // Crea registro si no existe
    await setDoc(
      doc(db, "users", user.uid),
      {
        id: user.uid, // ⚠️ agrega este campo también
        nombre: user.displayName,
        email: user.email,
        empresa: "No especificada",
        giro: "Desconocido",
        fechaRegistro: serverTimestamp(),
      },
      { merge: true }
    );

    window.location.href = "index.html";
  } catch (err) {
    alert("Error al iniciar con Google: " + err.message);
  }
};

$("btnGoogle").onclick = handleGoogleSignIn;
$("btnGoogleLogin").onclick = handleGoogleSignIn;

// 5. No hay redirección automática, ni sesión activa al entrar
console.log("Login listo — sin sesión activa por defecto.");
