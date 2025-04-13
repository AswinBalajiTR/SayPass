## **SayPass** – Voice is the New Password

### Inspiration
Till now, we’ve commonly used **patterns**, **numerical PINs**, or **fingerprint-based** passwords for device and app authentication. 

As an upgrade, **SayPass** introduces a smarter, more personalized way of authentication — **your voice**

Unlike many modern smartphones that recognize only **voice commands** , SayPass goes further by analyzing the **unique vocal frequency, pitch, and tone** of a person’s voice, something that's hard to imitate and unique to each individual.

---
###  What We Built 
**SayPass** is a dual-verification voice authentication system that:

- Verifies **who** is speaking using **ECAPA-TDNN** speaker embeddings.
- Verifies **what** is spoken using **Whisper** transcription.
- Grants access **only** when both the voiceprint and phrase match.

Say your passphrase, and SayPass checks:
1. Is it your **unique voice frequency**?
2. Did you say the **correct phrase**?

Only when both match, access is granted ✓

---

### Use Cases

- **Cybersecurity defense** – Adding a biometric voice layer to protect against unauthorized access  
- **Hands-free access** in vehicles, workstations, or AR/VR setups  
- **Voice-based smart lock access**  
- **Authentication for visually impaired users**   
- **Forensic voice analysis** – Matching suspect’s voice with crime scene audio evidence  


---

### What We Learned
- How to integrate **voice biometrics** using ECAPA-TDNN
- How to use **Whisper** for accurate transcription, even with accents
- The importance of combining **voice tone** + **spoken content** for high-security systems

---

### Challenges Faced 
- Background noise and **silent voice trimming**
- Fine-tuning thresholds to avoid **false accept** or **false reject**

---

### The Future
We envision SayPass as a secure, scalable system that can be used in:

- Mobile & Web Authentication
- Smart Home & IoT Devices
- Personalized AI Assistants

Because in the future...

> **Your voice should be your password.**
