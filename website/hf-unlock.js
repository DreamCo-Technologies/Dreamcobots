/* Unlock the 10 Hugging Face actions. Passcode and face stay on this device. */
(function () {
  const ACTIONS = window.HF_ACTIONS || [];
  const status = document.getElementById("unlock-status");
  const list = document.getElementById("action-list");
  const passForm = document.getElementById("passcode-form");
  const passInput = document.getElementById("passcode");
  const shareBox = document.getElementById("do-not-share");
  const cookieNote = document.getElementById("cookie-note");
  let open = sessionStorage.getItem("dreamco-unlocked") === "yes";

  function say(text) {
    if (status) status.textContent = text;
  }

  function render() {
    if (!list) return;
    list.replaceChildren();
    ACTIONS.forEach(function (item) {
      const card = document.createElement("article");
      card.className = "card";
      const title = document.createElement("h2");
      title.textContent = item.name;
      const about = document.createElement("p");
      about.textContent = item.about;
      const link = document.createElement("a");
      link.href = open ? item.href : "#unlock";
      link.textContent = open ? "Open" : "Unlock to open";
      if (!open) {
        link.setAttribute("aria-disabled", "true");
        link.addEventListener("click", function (event) {
          event.preventDefault();
          say("Use Google, Apple, a passcode, or face unlock on this device first.");
        });
      } else if (item.external) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
      card.append(title, about, link);
      list.append(card);
    });
  }

  function mark(how) {
    sessionStorage.setItem("dreamco-unlocked", "yes");
    open = true;
    say("Unlocked with " + how + ". Nothing was uploaded to Hugging Face.");
    render();
  }

  function bytesToB64(bytes) {
    let text = "";
    bytes.forEach(function (value) { text += String.fromCharCode(value); });
    return btoa(text);
  }

  function b64ToBytes(text) {
    return Uint8Array.from(atob(text), function (char) { return char.charCodeAt(0); });
  }

  async function hashPasscode(code, salt) {
    const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(code), "PBKDF2", false, ["deriveBits"]);
    const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", salt: salt, iterations: 150000, hash: "SHA-256" }, key, 256);
    return bytesToB64(new Uint8Array(bits));
  }

  async function saveOrCheckPasscode(code) {
    if (code.length < 4) {
      say("Use at least 4 characters. This passcode stays in this browser.");
      return;
    }
    const saved = localStorage.getItem("dreamco-passcode");
    if (!saved) {
      const salt = crypto.getRandomValues(new Uint8Array(16));
      const hash = await hashPasscode(code, salt);
      localStorage.setItem("dreamco-passcode", JSON.stringify({ salt: bytesToB64(salt), hash: hash }));
      mark("a passcode saved only in this browser");
      return;
    }
    const parsed = JSON.parse(saved);
    const hash = await hashPasscode(code, b64ToBytes(parsed.salt));
    if (hash === parsed.hash) mark("the passcode on this device");
    else say("That passcode does not match this browser.");
  }

  async function faceUnlock() {
    if (!window.PublicKeyCredential) {
      say("This browser cannot use face unlock. Use the passcode.");
      return;
    }
    const challenge = crypto.getRandomValues(new Uint8Array(32));
    const stored = localStorage.getItem("dreamco-face-id");
    try {
      if (stored) {
        await navigator.credentials.get({
          publicKey: {
            challenge: challenge,
            timeout: 60000,
            userVerification: "required",
            allowCredentials: [{ id: b64ToBytes(stored), type: "public-key" }],
          },
        });
      } else {
        const created = await navigator.credentials.create({
          publicKey: {
            challenge: challenge,
            rp: { name: "DreamCo Buddy" },
            user: {
              id: crypto.getRandomValues(new Uint8Array(16)),
              name: "buddy-device",
              displayName: "This device",
            },
            pubKeyCredParams: [{ type: "public-key", alg: -7 }, { type: "public-key", alg: -257 }],
            authenticatorSelection: { authenticatorAttachment: "platform", userVerification: "required" },
            timeout: 60000,
            attestation: "none",
          },
        });
        localStorage.setItem("dreamco-face-id", bytesToB64(new Uint8Array(created.rawId)));
      }
      mark("face or device passcode");
    } catch (error) {
      say("Face unlock did not finish. You can use the passcode instead.");
    }
  }

  function wireAccount(provider) {
    const button = document.getElementById(provider + "-login");
    if (!button) return;
    fetch("/api/auth/providers", { cache: "no-store" })
      .then(function (response) { return response.ok ? response.json() : Promise.reject(); })
      .then(function (body) {
        const found = (body.providers || []).find(function (item) { return item.provider === provider; });
        if (found && found.configured) button.href = "/api/auth/" + provider + "/start?next=/hf-unlock.html";
        else button.href = "sign-in.html#setup";
      })
      .catch(function () {
        button.href = "sign-in.html#setup";
      });
  }

  if (new URLSearchParams(location.search).get("status") === "success") mark("Google or Apple");
  if (passForm) {
    passForm.addEventListener("submit", function (event) {
      event.preventDefault();
      saveOrCheckPasscode(passInput.value);
      passInput.value = "";
    });
  }
  const face = document.getElementById("face-login");
  if (face) face.addEventListener("click", function (event) { event.preventDefault(); faceUnlock(); });
  wireAccount("google");
  wireAccount("apple");
  if (shareBox) {
    shareBox.checked = localStorage.getItem("dreamco-do-not-share") !== "no";
    shareBox.addEventListener("change", function () {
      localStorage.setItem("dreamco-do-not-share", shareBox.checked ? "yes" : "no");
    });
  }
  if (cookieNote && localStorage.getItem("dreamco-cookies") === "essential") cookieNote.hidden = true;
  const cookieButton = document.getElementById("cookies-essential");
  if (cookieButton) cookieButton.addEventListener("click", function () {
    localStorage.setItem("dreamco-cookies", "essential");
    if (cookieNote) cookieNote.hidden = true;
  });
  render();
})();
