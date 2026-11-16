import os
import streamlit as st


class VocabularyEntry:

  def __init__(self, german="", finnish="", example="", status=False):
    self.german = german
    self.finnish = finnish
    self.example = example
    self.status = status


def load_vocabulary(filename="sanat.txt"):
  if not os.path.exists(filename):
    return []
  with open(filename, "r", encoding="utf-8") as f:
    lines = f.readlines()

  thesaurus = []
  for line in lines:
    line = line.strip()
    if line:
      parts = line.split(";")
      if len(parts) >= 3:
        word = VocabularyEntry(
            german=parts[0], finnish=parts[1], example=parts[2], status=False
        )
        thesaurus.append(word)
  return thesaurus


st.title("Saksan sanapeli")

# Alustetaan tilamuuttujat istuntoon
if "vocab_list" not in st.session_state:
  st.session_state.vocab_list = load_vocabulary("sanat.txt")
if "score" not in st.session_state:
  st.session_state.score = 0
if "feedback" not in st.session_state:
  st.session_state.feedback = ""
if "game_over" not in st.session_state:
  st.session_state.game_over = False

# Sivupalkki tiedoston hallintaan
with st.sidebar:
  st.header("Asetukset")
  filename_input = st.text_input("Vokabeldatei:", value="sanat.txt")
  if st.button("Lataa tiedosto uudelleen"):
    st.session_state.vocab_list = load_vocabulary(filename_input)
    st.session_state.score = 0
    st.session_state.feedback = "Tiedosto ladattu!"
    st.session_state.game_over = False
    st.rerun()

vocab_list = st.session_state.vocab_list

if not vocab_list:
  st.warning(
      "Sanalistaa ei löytynyt tai se on tyhjä. Varmista, että 'sanat.txt'"
      " sijaitsee projektin kansiossa."
  )
else:
  # Etsitään sanat, joita ei ole vielä opittu
  uncompleted = [w for w in vocab_list if not w.status]

  if not uncompleted or st.session_state.game_over:
    st.success("Du hast alles richtig gemacht! Kaikki sanat käyty läpi.")
    if st.button("Aloita alusta"):
      for w in vocab_list:
        w.status = False
      st.session_state.game_over = False
      st.session_state.score = 0
      st.session_state.feedback = ""
      st.rerun()
  else:
    # Otetaan ensimmäinen oppimaton sana tarkasteluun
    current_word = uncompleted[0]

    st.write(f"Pisteet: {st.session_state.score} / {len(vocab_list)}")
    st.subheader(f"Das Wort (suomeksi): {current_word.finnish}")

    with st.form(key="quiz_form", clear_on_submit=True):
      translation = st.text_input(
          "Übersetzen Sie das Wort auf Deutsch (syötä 'beenden'"
          " lopettaaksesi):"
      )
      submit_button = st.form_submit_button(label="Vastaa")

      if submit_button:
        cleaned_translation = translation.strip().lower()

        if cleaned_translation in ["beenden", "lopeta"]:
          st.session_state.game_over = True
          st.rerun()
        elif translation.strip() == current_word.german:
          st.session_state.feedback = (
              f"Richtig!\n\nBeispiel: {current_word.example}"
          )
          current_word.status = True
          st.session_state.score += 1
          st.rerun()
        else:
          st.session_state.feedback = (
              f"Väärin. Oikea sana on: {current_word.german}\n\nBeispiel:"
              f" {current_word.example}"
          )
          st.rerun()

    if st.session_state.feedback:
      st.info(st.session_state.feedback)
