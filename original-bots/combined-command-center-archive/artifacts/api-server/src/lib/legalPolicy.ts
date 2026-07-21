/**
 * Versioned biometric & likeness policy shown to users BEFORE they may enroll a
 * voice/face or use any cloning feature. This is informational: it summarizes
 * the laws and obligations that govern voice/image cloning so a user gives
 * genuinely informed consent. It is NOT legal advice and is not a substitute for
 * a lawyer-reviewed Terms of Service / Privacy Policy.
 *
 * Bump POLICY_VERSION whenever the content changes; users must re-acknowledge a
 * new version before continuing to use cloning features.
 */

export const POLICY_KEY = "biometric-cloning-policy";
export const POLICY_VERSION = "2026-05-29.1";

export interface LawSummary {
  name: string;
  jurisdiction: string;
  summary: string;
}

export interface PolicySection {
  heading: string;
  body: string;
}

export interface BiometricPolicy {
  key: string;
  version: string;
  title: string;
  intro: string;
  laws: LawSummary[];
  sections: PolicySection[];
  userPromises: string[];
  disclaimer: string;
}

export const BIOMETRIC_POLICY: BiometricPolicy = {
  key: POLICY_KEY,
  version: POLICY_VERSION,
  title: "Voice & Image Cloning — Consent, Rights & Legal Acknowledgment",
  intro:
    "DreamCo can clone voices and faces (likeness) at high quality, but only with the verifiable, informed consent of the person being cloned. Cloning a person's voice or image without authorization can be illegal and can cause real harm. Before you enroll a voice or face, or use any cloning feature, you must read and accept the following. You may only clone (a) yourself, or (b) a person who has given you explicit, documented permission.",
  laws: [
    {
      name: "Illinois Biometric Information Privacy Act (BIPA)",
      jurisdiction: "Illinois, USA",
      summary:
        "Requires written, informed consent before collecting or storing biometric identifiers (including voiceprints and face geometry). Provides a private right of action with statutory damages per violation.",
    },
    {
      name: "Texas CUBI & Washington HB 1493",
      jurisdiction: "Texas / Washington, USA",
      summary:
        "State biometric privacy laws requiring notice and consent before capturing biometric identifiers and limiting their disclosure and retention.",
    },
    {
      name: "GDPR Article 9 (special category data) & Articles 6–7 (consent)",
      jurisdiction: "European Union / EEA",
      summary:
        "Biometric data used to uniquely identify a person is a special category requiring explicit consent (or another Art. 9 basis). Consent must be freely given, specific, informed, and revocable.",
    },
    {
      name: "CCPA / CPRA",
      jurisdiction: "California, USA",
      summary:
        "Treats biometric information as sensitive personal information, granting rights to notice, access, deletion, and to limit use; requires disclosure of collection and purpose.",
    },
    {
      name: "EU AI Act — synthetic media transparency",
      jurisdiction: "European Union",
      summary:
        "Requires that AI-generated or manipulated audio/image/video (deepfakes) be clearly disclosed as artificially generated.",
    },
    {
      name: "Tennessee ELVIS Act & right-of-publicity / NO FAKES-style laws",
      jurisdiction: "USA (state right of publicity; proposed federal)",
      summary:
        "Protect a person's voice and likeness from unauthorized commercial use or simulation. Unauthorized cloning of someone's voice or image can violate their right of publicity.",
    },
  ],
  sections: [
    {
      heading: "1. Consent is mandatory and verifiable",
      body: "You may only enroll and clone a voice or face that is your own, or one you have explicit, documented permission to use. By enrolling, you affirm the sample is yours or that you hold written authorization from the person it depicts. DreamCo records each consent with your account, the modality, and a timestamp.",
    },
    {
      heading: "2. Enrollment ('sign in with your voice/image')",
      body: "To use cloning, you first enroll your own voice and/or image as a reference sample. Cloning is restricted to modalities you have personally enrolled and consented to. You cannot clone a voice or face you have not enrolled.",
    },
    {
      heading: "3. Disclosure of synthetic media",
      body: "Audio, images, or video produced by cloning are AI-generated. Where required by law (e.g., the EU AI Act), you must disclose that the output is artificially generated and not a genuine recording of the person.",
    },
    {
      heading: "4. Prohibited uses",
      body: "No fraud, impersonation, harassment, defamation, non-consensual intimate imagery, election or financial deception, or any use that violates another person's rights or applicable law. Violations may result in suspension and may be reported as required by law.",
    },
    {
      heading: "5. Revocation & deletion",
      body: "You can revoke an enrollment at any time, which disables cloning for that modality going forward. You may request deletion of your enrolled samples and consent records.",
    },
    {
      heading: "6. Your responsibility",
      body: "You are solely responsible for ensuring you have the legal right to clone any voice or image you submit, and for complying with all laws in your jurisdiction.",
    },
  ],
  userPromises: [
    "I will only clone my own voice/image, or one I have explicit written permission to use.",
    "I understand cloned output is AI-generated and I will disclose it as required by law.",
    "I will not use cloning for fraud, impersonation, or any unlawful or harmful purpose.",
    "I understand I can revoke my enrollment and request deletion at any time.",
  ],
  disclaimer:
    "This summary is provided for transparency and informed consent. It is informational only, is not legal advice, and is not exhaustive. Laws vary by jurisdiction and change over time. DreamCo operators must publish their own lawyer-reviewed Terms of Service and Privacy Policy before offering cloning to the public.",
};
