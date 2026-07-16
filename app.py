import streamlit as st
import requests

st.set_page_config(page_title="VERIDOC — Assistant biomédical", page_icon="🩺")

st.title("🩺 Assistant biomédical avec verdict calibré")
st.markdown("Pose une question médicale et fournis le contexte scientifique associé.")

API_URL = "https://veridoc-api.onrender.com/predict"  # remplace par ta propre API Render de la Partie 2

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("prediction_form"):
    question = st.text_input("Question", placeholder="Ex: Does aspirin reduce fever in adults?")
    context = st.text_area("Contexte médical", height=150,
                            placeholder="Colle ici le passage scientifique qui sert de preuve...")
    threshold = st.slider("Seuil de confiance minimum", 0.0, 1.0, 0.6)
    submitted = st.form_submit_button("Analyser")

if submitted:
    if not question.strip() or len(context.strip()) < 10:
        st.warning("⚠️ Merci de remplir la question et un contexte suffisamment long.")
    else:
        with st.spinner("Analyse en cours..."):
            try:
                response = requests.post(API_URL, json={
                    "question": question, "context": context, "threshold": threshold
                }, timeout=60)
                data = response.json()
            except Exception as e:
                st.error(f"Erreur de connexion à l'API : {e}")
                data = None

        if data:
            verdict = data.get("verdict", "inconnu")
            confidence = data.get("confidence", 0)

            if verdict == "abstention":
                st.warning(f"🟠 Abstention — le modèle n'est pas assez confiant ({confidence:.0%})")
            elif verdict == "yes":
                st.success(f"✅ Oui — confiance : {confidence:.0%}")
            elif verdict == "no":
                st.error(f"❌ Non — confiance : {confidence:.0%}")
            else:
                st.info(f"🤔 Peut-être — confiance : {confidence:.0%}")

            st.caption(data.get("disclaimer", "⚠️ Ceci n'est pas un avis médical."))

            st.session_state.history.append(f"{question[:50]}... → {verdict} ({confidence:.0%})")

if st.session_state.history:
    st.subheader("Historique de la session")
    for entry in reversed(st.session_state.history[-10:]):
        st.text(entry)
