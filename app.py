import glob
import os
import streamlit as st


class VocabularyEntry:

  def __init__(self, german="", finnish="", example="", status=False):
    self.german = german
    self.finnish = finnish
    self.example = example
    self.status = status


def get_available_files():
  # Etsitään kaikki .txt-tiedostot samasta kansiosta, paitsi requirements.txt
  txt_files = glob.glob("*.txt")
  return sorted([f for f in txt_files if f != "requirements.txt"])


def load_vocabulary(filename):
  if not filename or not os.path.exists(filename):
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


st.title("Üben Sie die Worte.")

# Haetaan kansiossa olevat sanalistat
available_files = get_available_files()

# Sivupalkki sanalistan valintaan
with st.sidebar:
  st.header("Wortliste")

  if not available_files:
    st.warning("Keine .txt-Vokabellisten im Verzeichnis gefunden.")
    selected_file = None
  else:
    # Vetovalikko (selectbox) sanalistoille
    selected_file = st.selectbox("Liste auswählen:", available_files)

    # Tarkistetaan, onko käyttäjä vaihtanut tiedostoa vetovalikosta
    if (
        "current_file" not in st.session_state
        or st.session_state.current_file != selected_file
    ):
      st.session_state.current_file = selected_file
      st.session_state.vocab_list = load_vocabulary(selected_file)
      st.session_state.score = 0
      st.session_state.feedback = ""
      st.session_state.game_over = False

    if st.button("Liste neu laden"):
      st.session_state.vocab_list = load_vocabulary(selected_file)
      st.session_state.score = 0
      st.session_state.feedback = ""
      st.session_state.game_over = False
      st.rerun()

# Alustetaan loput tilamuuttujat varmuuden vuoksi
if "vocab_list" not in st.session_state:
  st.session_state.vocab_list = []
if "score" not in st.session_state:
  st.session_state.score = 0
if "feedback" not in st.session_state:
  st.session_state.feedback = ""
if "game_over" not in st.session_state:
  st.session_state.game_over = False

vocab_list = st.session_state.vocab_list

# Varsinainen peli
if not selected_file:
  st.info("Mindestens eine .txt-Wortliste auf GitHub hochladen, um zu starten.")
elif not vocab_list:
  st.warning(
      f"Die datei '{selected_file}' ist leer oder falsch formatiert."
  )
else:
  uncompleted = [w for w in vocab_list if not w.status]

  if not uncompleted or st.session_state.game_over:
    st.success("Es war so eine Runde!")
    if st.button("Neu anfangen"):
      for w in vocab_list:
        w.status = False
      st.session_state.game_over = False
      st.session_state.score = 0
      st.session_state.feedback = ""
      st.rerun()
  else:
    current_word = uncompleted[0]

    st.write(f"Wertung: {st.session_state.score} / {len(vocab_list)}")
    st.subheader(f"{current_word.finnish}")

    with st.form(key="quiz_form", clear_on_submit=True):
      translation = st.text_input(
          "Übersetzen Sie das Wort auf Deutsch ('beenden' beendet):"
      )
      submit_button = str_lit_submit = st.form_submit_button(label="Antworten")

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
              f"Falsch. Das richtige Wort ist: {current_word.german}\n\nBeispiel:"
              f" {current_word.example}"
          )
          st.rerun()

    if st.session_state.feedback:
      st.info(st.session_state.feedback)