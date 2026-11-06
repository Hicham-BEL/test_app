import random
import streamlit as st

st.set_page_config(page_title="Planning Poker", page_icon="🃏")

CARTES = ["1", "2", "3", "5", "8", "13", "20", "40", "100", "☕"]


# Dictionnaire partagé entre tous les joueurs connectés au lien
@st.cache_resource
def get_salons():
    return {}


salons = get_salons()

# --- ÉCRAN 1 : ACCUEIL (CRÉER OU REJOINDRE UN SALON) ---
if "code" not in st.session_state:
    st.title("🃏 Planning Poker")
    pseudo = st.text_input("Votre pseudo").strip()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Créer une session")
        if st.button("➕ Créer un nouveau salon", type="primary", use_container_width=True):
            if pseudo:
                code = str(random.randint(1000, 9999))
                salons[code] = {
                    "createur": pseudo,
                    "votes": {pseudo: None},
                    "revele": False,
                    "tour": 1,
                    "regle": "strict"
                }
                st.session_state.code = code
                st.session_state.pseudo = pseudo
                st.rerun()
            else:
                st.warning("Entrez un pseudo d'abord.")

    with col2:
        st.subheader("Rejoindre une session")
        code_saisi = st.text_input("Code du salon (ex: 1234)").strip()
        if st.button("🚪 Rejoindre le salon", use_container_width=True):
            if pseudo and code_saisi in salons:
                salons[code_saisi]["votes"][pseudo] = None
                st.session_state.code = code_saisi
                st.session_state.pseudo = pseudo
                st.rerun()
            else:
                st.error("Pseudo manquant ou code de salon invalide.")

# --- ÉCRAN 2 : SALON DE VOTE EN SIMULTANÉ ---
else:
    code = st.session_state.code
    pseudo = st.session_state.pseudo
    salon = salons.get(code)

    if not salon:
        del st.session_state.code
        st.rerun()

    est_createur = (pseudo == salon["createur"])

    # Entête avec le code d'invitation
    st.info(f"🔑 **Code du salon à partager :** `{code}`  |  👤 **Joueur :** {pseudo} {'(Créateur)' if est_createur else ''}")

    # Choix de la carte (US-012)
    st.write("### 1. Choisissez une carte :")
    cols = st.columns(len(CARTES))
    for i, carte in enumerate(CARTES):
        est_choisie = (salon["votes"].get(pseudo) == carte)
        if cols[i].button(carte, type="primary" if est_choisie else "secondary", disabled=salon["revele"]):
            salon["votes"][pseudo] = carte
            st.rerun()

    st.divider()

    # Zone rafraîchie toutes les 2 secondes pour tous les joueurs du salon
    @st.fragment(run_every=2)
    def plateau_en_direct():
        st.write(f"### 2. Votes du salon (Tour {salon['tour']} — Règle : {salon['regle']})")

        # Affichage des joueurs et de leurs cartes (US-013)
        for joueur, vote in salon["votes"].items():
            if salon["revele"]:
                etat = f"🃏 **{vote}**" if vote else "❓ Pas voté"
            else:
                etat = "✅ A voté" if vote else "⏳ En réflexion..."
            st.write(f"- **{joueur}** : {etat}")

        # Résultat selon la règle stricte d'unanimité (US-02 et US-03)
        if salon["revele"]:
            votes_exprimes = [v for v in salon["votes"].values() if v is not None]
            if len(votes_exprimes) == len(salon["votes"]) and len(set(votes_exprimes)) == 1:
                st.success(f"🎉 Unanimité sur la carte **{votes_exprimes[0]}** ! Fonctionnalité validée.")
            else:
                st.warning("⚠️ Pas d'unanimité. Discutez et lancez le tour suivant.")

        # Boutons réservés au créateur (US-013)
        if est_createur:
            st.write("---")
            c1, c2 = st.columns(2)
            if c1.button("👁️ Afficher / Cacher les cartes", use_container_width=True):
                salon["revele"] = not salon["revele"]
                st.rerun()
            if c2.button("🔄 Nouveau tour / Vote suivant", use_container_width=True):
                salon["revele"] = False
                salon["tour"] += 1
                for j in salon["votes"]:
                    salon["votes"][j] = None
                st.rerun()

    plateau_en_direct()

    if st.button("Quitter le salon"):
        del st.session_state.code
        st.rerun()
