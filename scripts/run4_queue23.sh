#!/bin/bash
# Des que la feuille de segB est lue par notre modele, produire LA MEME BANDE vue par lui, sur la meme ligne et la
# meme geometrie que celle donnee a Lilian. C est le test decisif de la ligne : un second lecteur, entraine sur un
# autre segment et qui n a jamais vu celui-ci, voit-il les memes lettres au meme endroit ?
# Plus une mesure : reponse de notre modele DANS les taches de la ligne contre le ruban qui les entoure.
export PATH="$HOME/.local/bin:$PATH"; cd ~/vesuvius
H=/home/slusarska_holding/vesuvius; lab=auto_grown_20260220174252405
IMG="/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/images/arbitrage/2026-09-23_ligne"
{
  echo "== queue23 attente de la recouture de segB $(date +%T)"
  for i in $(seq 1 240); do [ -f "$H/predictions/b841_human7n_feuille.tif" ] && break; sleep 60; done
  [ -f "$H/predictions/b841_human7n_feuille.tif" ] || { echo "== queue23 abandon"; exit 0; }
  sleep 30
  echo "== queue23 debut $(date +%T)"
  HB=800 RED=2 MORC=2100 XMIN=4000 XMAX=16600 PRED=$H/predictions/b841_human7n_feuille.tif \
    villa/vesuvius/.venv/bin/python /home/slusarska_holding/vesuvius/bande_ligne.py $lab 8064 9364 8752 13552 \
    "$IMG/2026-09-23_ligne_a_lire_NOUS.png"
  echo "-- mesure du second lecteur sur les taches de la ligne $(date +%T)"
  villa/vesuvius/.venv/bin/python /home/slusarska_holding/vesuvius/verdict_ligne.py $lab
  echo "== queue23 fin $(date +%T)"
} >> logs/run4_queue23.log 2>&1
