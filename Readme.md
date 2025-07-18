# 🔐 FHIR Lesson 20 – Building a Simple SMART on FHIR Application

Welcome to **Lesson 20** of the FHIR curriculum: _Building a Simple SMART on FHIR Application_. This lesson introduces students to secure FHIR data access using SMART on FHIR protocols and the OAuth 2.0 Authorization Code Flow with PKCE. Students will build and test progressively richer terminal-based applications, starting with basic login and patient data retrieval, and advancing to scoped, patient-facing FHIR apps.

👨‍🏫 _Instructors:_  
- **Patrick W. Jamieson, M.D.**, Technical Product Manager  
- **Russ Leftwich, M.D.**, Senior Clinical Advisor, Interoperability  

---

## 🎯 Lesson Objectives

- Understand how SMART on FHIR leverages OAuth 2.0 to authorize FHIR API calls
- Use the Authorization Code Flow with PKCE in a terminal application
- Launch and manage browser redirects for login and token exchange
- Modularize code for authentication (`smart_auth.py`) and API interaction (`fhir_client.py`)
- Apply SMART scopes to simulate user-specific access to patient data

---

## 🛠 Prerequisites

Before starting, clone and run the [SecureDockerFHIR](https://github.com/pjamiesointersystems/SecureDockerfhir) environment, which provides:

- A secure IRIS for Health FHIR server
- HTTPS via SSL certificates
- A configured Web Gateway for SMART token flow

ℹ️ **Token-based access requires HTTPS**. Plain HTTP connections will be rejected—even with valid tokens:contentReference[oaicite:0]{index=0}.

---

## 🧪 Lab Applications (Stepwise Progression)

### 🚀 Application 1: Basic SMART on FHIR Login
- Launches a browser for user login and authorization
- Receives `code` via `localhost:8765` mini-HTTP server
- Exchanges the code for an access token
- Retrieves a single Patient resource using the token

### 🔧 Application 2: Modular SMART App
- Code is split into two modules:
  - `smart_auth.py`: handles OAuth 2.0 login and token exchange
  - `fhir_client.py`: makes authenticated FHIR API calls
- Displays a list of patients by name and FHIR ID

### 📈 Application 3: Observations for a Selected Patient
- Allows user to select a patient
- Fetches all related Observation resources
- Displays key details: LOINC codes, values, units

### 🔐 Application 4: Scoped Patient Portal App
- Uses SMART scopes such as:
  - `patient/Patient.read`
  - `patient/Observation.read`
- Simulates a real-world patient portal
- Enforces access control and demonstrates scope violations

---

## 🧠 Auth0 and Patient Context

To simulate a real patient-facing app, the access token must include the FHIR `patient_id`. This requires:

- Enabling `user_metadata` in Auth0
- Using an Auth0 **Post-Login Action**:
```javascript
exports.onExecutePostLogin = async (event, api) => {
  const patient = event.user.user_metadata?.patient;
  if (patient) {
    const ns = 'https://fhir.example.com/claims/';
    api.idToken.setCustomClaim(`${ns}patient`, patient);
    api.accessToken.setCustomClaim(`${ns}patient`, patient);
  }
};
