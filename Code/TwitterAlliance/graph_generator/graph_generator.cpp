#include<iostream>
#include <fstream>
#include <map>
#include <string>
using namespace std;

int main() {

	string usuario = "", primerUsuario = " ", line;
	ifstream file;
	ofstream gephiN, gephiA;

	file.open("Top100_Global.txt");

	map<string, int> nodos;
	
	int counter = 0;

	if (file.is_open())
	{
		//abrimos el fichero al que vamos a volcar la info
		gephiN.open("Nodos.csv");
		gephiN << "Id;Label" << endl;
		gephiA.open("Aristas.csv");
		gephiA << "Source;Target;Type" << endl;

		while (getline(file, line))
		{
			map<string, int>::iterator it = nodos.begin();

			int c = 0;
			size_t pos = 0;

			//en cuanto al usuario principal de la linea:
			pos = line.find(" ");
			primerUsuario = line.substr(0, pos - 1);

			it = nodos.find(primerUsuario);
			if (it == nodos.end()) { //nunca lo habíamos leido antes
				if (primerUsuario.find("@") != std::string::npos){ //si este correo tiene un @
					nodos.insert(pair<string, long long int>(primerUsuario, counter));
					//volcamos la info del nuevo nodo a gephi
					gephiN << counter << ";" << primerUsuario << endl;
					counter++;
				}
			}

			line = line.substr(pos + 1, line.length());
			while ((pos = line.find(" ")) != string::npos){ //pos es el numero de bits hasta un espacio
				usuario = line.substr(0, pos); //correo tiene la string desde la posición 0 hasta el fin de linea

				it = nodos.find(usuario);
				if (it == nodos.end()) { //nunca lo habíamos leido antes
					if (usuario.find("@") != std::string::npos){ //si este correo tiene un @
						nodos.insert(pair<string, long long int>(usuario, counter));
						//volcamos la info del nuevo nodo a gephi
						gephiN << counter << ";" << usuario << endl;
						counter++;
					}
				}

				//nuevas aristas
					if (usuario.find("@") != std::string::npos){
						gephiA << nodos[primerUsuario] << ";" << nodos[usuario] << ";" << "Undirected" << endl;
					}


					line = line.substr(pos + 1, line.length()); //recorto la cadena
				c++;
			}
		}
	}

	gephiN.close();
	gephiA.close();
	file.close();

	return 0;
}