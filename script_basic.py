#!/usr/bin/python3

from Bio.PDB import *
from sys import argv, exit
import os

io = PDBIO()
os.system("rm temp*.pdb")

def superimpose(fix_chain,mov_chain,apply_chain):
	"""
	Superimpose peptide chain mov_chain on fix_chain with Biopython superimposer, and apply movement to chain.
	"""
	sup = Superimposer()

	#//Obtenir una llista d'atoms-objects per a cada cadena
	fix_atoms = list(fix_chain.get_atoms())
	mov_atoms = list(mov_chain.get_atoms())
	#//Fer superimposicio
	sup.set_atoms(fix_atoms	,mov_atoms)

	sup.apply(apply_chain)
	return apply_chain

count = 0
def recursive(chain_ob, camefrom, interactions, allpdb, count):
	"""
	NOTA A MARTA: Aquesta subrutina, benvolguda Marta, potser ens solucioni gran part del treball o potser ens peti l'ordinador. L'important es que sortirem de dubtes
	L'he comentat molt perque la puguis entendre facil i rapidament
	ALERTA!!!!: si visualitzes els resultats a chimera es veuran malament la majoria dels cops, doncs aquest algoritme te tendencia a repetir subunitats. I si dues subunitats estan molt a prop, chimera les separa
	"""
	count += 1
	chainame = chain_ob.get_id()
	#//Tancament de seguretat per evitar que se li vagi l'olla
	if count == 5:
		exit()

	#Iterate throught the chains which interact with the present chain
	for chainteracting in interactions[chainame]:
		#If this loop corresponds to the already superimposed chain where the present chain_ob comes from, skip it
		if chainteracting == camefrom:
			continue

		#Extract the pdb where chain_ob and chainteracting are both toghether
		pdbname = interactions[chainame][chainteracting]
		pdb_ob = allpdb[pdbname]
		#chaintomove: chain of the same type than chain_ob in the pdb-file
		chaintomove = pdb_ob[0][chainame]
		#aplichain: chain that will be moved to interact with chain_ob
		applychain = pdb_ob[0][chainteracting]
		#Superimpose
		appliedchain = superimpose(fix_chain = chain_ob, mov_chain = chaintomove, apply_chain = applychain)

		#Save appliedchain (the moved one) in a new pdb
		io.set_structure(appliedchain)
		tempname = "temp" + str(count) + ".pdb"
		io.save(tempname)

		#Repeat process for appliedchain
		recursive(appliedchain, chainame, interactions, allpdb, count)

# Create a PDBparser object
parser = PDBParser(PERMISSIVE = 1)

##########################################
##Store Relations between files and chains
##########################################

"""
Dictionary and list index:
	1. Allpdb:
		keys: input pdb filenames
		values: Structure pdb object from file

	2. Subunits: all chain names introduced
	3. Chainsbyfile: 
		keys: input pdb filenames
		values: list of chain-objects in pdb file
	4. Interactions: 
		key: chain name
		value: list of chain names wich interacts with

"""

#Create a structure object for every file and store them as values in a dictionary with name of file as key
allpdb = { filename : parser.get_structure(filename, filename) for filename in argv if argv.index(filename) != 0}

#Store all chain id in a set. Create a dictionary where every filename has a list of chain-objects as values
subunits = set()
chainsbyfile = {}
for pdb in allpdb:
	chainsbyfile[pdb] = list()
	for subunit in allpdb[pdb].get_chains():
		chainsbyfile[pdb].append(subunit)
		subunits.add(subunit.get_id())

# Create a dictionary with all the subunits as keys and, as values, a list with the subunits which interacts with
# The list is a list of dictionaries, becaise every chain id has a reference to the pdb were was found
###########NOTA A DAVID: Hi ha d'haver una forma millor de fer aixo######################### 
######## MARTA: He afegit d'on venen les chains (és a dir de quin pdb surten). Sinó era info que no et portava enlloc
######## DAVID: Em sembla una bona idea, pero ho he canviat a diccionaris perque sia mes optim. Fer una llista de diccionaris d'una entrada es molt absurd
interactions = {}
intset = dict()

for element in subunits: 
	for filename in allpdb:
		chainames = [ a.get_id() for a in chainsbyfile[filename] ]
		if element in chainames:
			index = chainames.index(element)
			if index == 0:
				intset[chainames[1]] = filename
				
			else:
				intset[chainames[0]] = filename
	interactions[element] = intset
	intset = dict()

#print("allpdb: ",allpdb)
#print("subunits: ",subunits)
#print("chainsbyfile: ",chainsbyfile)
#print("interactions: ",interactions)

"""
//NOTA A SANDVITX: He canviat els pdbs que utiltzem com a probes pels que fan servir Oriol i Alvaro. Perque? perque no hi havia caigut en que, malgrat estiguin en fitxers separats, les nostres
cadenes ja estan positionades on els toca, d'ons venen d'un fitxer comu
Ara surten un munt de warnings, pero no t'alarmis, funciona igualment. Es perque els pdbs que utilitzen Alvaro i Oriol els falta una columna 
"""

#//Sobre com fer el pdb output. No he trobat manera humana de fer-ho d'una forma mes neta. Si en trobes una millor, fes'la, pero no t'hi matis buscant. Ja he perdut jo prou temps com perque t'hi matis tu ara
#//MARTA al habla: Ho deixo de mostra per no carregar-m'ho al intentar fer les iteracions per arribar a la macromolècula. 
#io.set_structure(chainsbyfile["AB.pdb"][0])
#io.save("temp1.pdb")
#io.set_structure(chainsbyfile["AB.pdb"][1])
#io.save("temp2.pdb")
#moved_chain = superimpose(chainsbyfile["AB.pdb"][0], chainsbyfile['AD.pdb'][0], chainsbyfile['AD.pdb'][1])
#io.set_structure(moved_chain)
#io.save("temp3.pdb")
#os.system("cat temp*.pdb > krosis.pdb")

"""
# For each pdb we use the first chain as the fixed chain (reference) and save the second one
# We look for the other chains interacting with the fixed one and we move them
# Generate a pdb with the join interactions
# In each iteration we check if the superimposition has aleready been done, in that case we skip the file
predone = set()
done = set()
count = 2

for option in [[0,1],[1,0]]:
	for pdbname in chainsbyfile: 
		io.set_structure(chainsbyfile[pdbname][option[0]])
		io.save("temp1.pdb")
		io.set_structure(chainsbyfile[pdbname][option[1]])
		io.save("temp2.pdb")

		predone.add(pdbname)
		fixchain = chainsbyfile[pdbname][option[0]].get_id()
		interactwith = interactions[fixchain]
		for pdb2 in interactwith:
			pdbinteract = interactwith[pdb2]
			done = predone.copy()
			done.add(pdbinteract)
			if len(predone) == len(done): 
				continue
			else:
				count += 1
				testwhere = chainsbyfile[pdbinteract][option[0]].get_id()
				print(testwhere)
				if testwhere == fixchain:
					posfix = option[0]
					posmov = option[1]
				else:
					posfix = option[1]
					posmov = option[0]
				#print(pdbname, option[0], pdbinteract, posfix, pdbinteract, posmov)
				moved_chain = superimpose(chainsbyfile[pdbname][0], chainsbyfile[pdbinteract][posfix], chainsbyfile[pdbinteract][posmov])
				io.set_structure(moved_chain)
				tempname = "temp" + str(count) + ".pdb"
				io.save(tempname)
		predone = done
	os.system("cat temp*.pdb > krosis.pdb")
"""


#//Camp de proves

#Obtain a random pdb interactino file
seed = list(allpdb.keys())[0]

#Iterate over pdb seed file chains
for chain in chainsbyfile[seed]:
	recursive(chain, chainsbyfile[seed][1].get_id(), interactions, allpdb, count)
