class Chord:

    def __init__(self):
        self.lista = []

    def join(self,node):
    
    def insert(self,newPeer):
        #buscar el lugar donde va el nodo e ingresarlo al anillo
        for i,elem in zip(len(self.lista),lista)):
            if newPeer.getId() < elem.getId():
                aux  = self.lista[0:i]
                aux2 = self.lista[i:]
                aux.append(newPeer) 
                self.lista = aux + aux2
                break
        
