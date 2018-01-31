#include<iostream>
#include <fstream>
#include <map>
#include <string>
using namespace std;

int main() {

	string usuario = "", primerUsuario = " ", line, tipo = "Undirected", country;
	char op;
	int counter = 0;
	bool extraInfo = false;

	ifstream file, fileExtra;
	ofstream gephiN, gephiA;

	map<string, string> info;
	map<string, int> nodos;


	cout << "------------- THE TWITTER ALLIANCE -------------" << endl;
	cout << "¿De que pais quieres generar la red? "<< endl;
	cout <<	"Por favor, escribelo en Ingles, minusculas y si son varias palabras, con un guion bajo entre ellas" << endl;
	cout << "Por ejemplo, united_kingdom, spain, global..." << endl;
	getline(cin, country);

	cout << "¿Que tipo de red quieres generar?, introduzca D (Dirigida) o N (No dirigida): ";

	do {
		cin >> op;
		if  (toupper(op) != 'D' && toupper(op) != 'N') cout << "Type it again, please: ";
	}while (toupper(op) != 'D' && toupper(op) != 'N');


	if (toupper(op) == 'D') tipo = "Directed";

	cout << "¿Necesita adjuntar mas informacion de cada usuario (localizacion, numero de tweets publicados...)?, introduzca S (Si) o N (No): ";
	cin >> op;

	if (toupper(op) == 'S') {
		fileExtra.open("Top100_" + country + "_friendships_users.txt");


		if (fileExtra.is_open()){
					while (getline(fileExtra, line)){
						size_t pos = 0;
						//en cuanto al usuario principal de la linea:
						pos = line.find(" ");
						primerUsuario = line.substr(0, pos - 1);
						line = line.substr(pos, line.length());
						info.insert(pair<string, string>(primerUsuario, line));
					}
			extraInfo = true;
		}else cout << "Por favor, asegurese de que ha introducido bien el nombre del pais cuya red quiere analizar, ademas de que ha copiado el archivo que contiene la informacion adicional de cada usuario en la carpeta actual." << endl;
	}

	file.open("Top100_" + country + "_friendships.txt");


	if (file.is_open())
	{
		//abrimos el fichero al que vamos a volcar la info
		gephiN.open("Nodos.csv");
		if (extraInfo) gephiN << "Id Label Country Followings Followers Tweets lat lng Favourites" << endl;
		else gephiN << "Id Label" << endl;
		gephiA.open("Aristas.csv");
		gephiA << "Source Target Type" << endl;

		while (getline(file, line))
		{
			map<string, int>::iterator it = nodos.begin();

			int c = 0;
			size_t pos = 0;

			//en cuanto al usuario principal de la linea:
			pos = line.find(" ");
			primerUsuario = line.substr(0, pos - 1);

			it = nodos.find(primerUsuario);
			if (it == nodos.end()) { //nunca lo hab�amos leido antes
				if (primerUsuario.find("@") != std::string::npos){ //si este correo tiene un @
					nodos.insert(pair<string, long long int>(primerUsuario, counter));
					//volcamos la info del nuevo nodo a gephi

					if (extraInfo) gephiN << counter << " " << primerUsuario << info[primerUsuario] << endl;
					else gephiN << counter << " " << primerUsuario << endl;
					counter++;
				}
			}

			line = line.substr(pos + 1, line.length());
			while ((pos = line.find(" ")) != string::npos){ //pos es el numero de bits hasta un espacio
				usuario = line.substr(0, pos); //correo tiene la string desde la posici�n 0 hasta el fin de linea

				it = nodos.find(usuario);
				if (it == nodos.end()) { //nunca lo hab�amos leido antes
					if (usuario.find("@") != std::string::npos){ //si este correo tiene un @
						nodos.insert(pair<string, long long int>(usuario, counter));
						//volcamos la info del nuevo nodo a gephi

						if (extraInfo) gephiN << counter << " " << usuario << info[usuario] << endl;
						else gephiN << counter << " " << usuario << endl;
						counter++;
					}
				}

				//nuevas aristas entre el usuario principal y el que acabamos de leer
					if (usuario.find("@") != std::string::npos){
						gephiA << nodos[primerUsuario] << " " << nodos[usuario] << " " << tipo << endl;
					}


					line = line.substr(pos + 1, line.length()); //recorto la cadena
				c++;
			}
		}

		cout << "Nodos.csv generado..." << endl;
		cout << "Aristas.csv generado..." << endl;
	}

	gephiN.close();
	gephiA.close();
	file.close();


	return 0;
}
