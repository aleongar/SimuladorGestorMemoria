import sys
import time
from abc import ABC, abstractmethod

class Process: #struct
    """
    Clase que representa un proceso
    
    Attributes:
        name (str): Nombre del proceso
        arribalTime (int): Momento de llegada del proceso
        memory (int): Memoria que ocupa el proceso
        execTime (int): Duración del proceso en memoria
    """
    def __init__(self, name: str, arribalTime: int, memory: int, execTime: int):
        """Constructor general del proceso
        
        Args:
            name (str): Nombre del proceso
            arribalTime (int): Momento de llegada del proceso
            memory (int): Memoria que ocupa el proceso
            execTime (int): Duración del proceso en memoria
        """
        self.name = name
        self.execTime = execTime
        self.memory = memory
        self.arribal = arribalTime

    def __str__(self) -> str:
        """Método para imprimir el proceso.

        Returns:
            str: String descriptivo del proceso.
        """
        return f"ID:{self.name}, Memory:{self.memory}, Time:{self.arribal}, Duration:{self.execTime}"

class ProcessBuffer:
    """Clase que representa un buffer de procesos.
    Generalmente, esta clase se usa para procesos que no han podido entrar y se quedan en cola.
    
    Attributes:
        processList (list): Lista de procesos en el buffer
    """
    def __init__(self, procList: list = []) -> None:
        """Constructor general de la clase, añade procesos al buffer en caso de ser necesario

        Args:
            procList (list, optional): Lista de procesos a añadir a la cola. Defaults to [].
        """
        self.processList = []
        for process in procList:
            self.addToBuffer(process)

    def addToBuffer(self, process: Process):
        """Método para añadir un proceso al buffer

        Args:
            process (Process): proceso a ser añadido
        """
        self.processList.append(process)

    def getNextProcess(self, maxSpace):
        """Detecta el proceso que debe de ser añadido como siguiente
        debido a que este puede ser que no quepa en la cola dada

        Args:
            maxSpace (int): espacio máximo que se puede añadir en el proceso

        Returns:
            Process: proceso que se puede añadir
            None: en caso de que no se pueda añadir ninguno
        """
        for i, process in enumerate(self.processList):
            if process.memory <= maxSpace:
                return self.processList.pop(i)

class InsuficientFragmentSpaceError(Exception): #exception
    """Error que ocurre cuando no se ha podido añadir el proceso por falta de espacio
    """
    def __init__(self, *args: object) -> None:
        super().__init__("Insuficient space in fragment")

class PageSpace:
    """Clase que representa un espacio de memoria
    Por defecto, pone su posición inicial en 0 y su posición final, el espacio que ocupa el proceso de dentro -1
    
    Attributes:
        space (int): Espacio que ocupa el fragmento
        process (Process): Proceso que está en este espacio de memoria. Defaults to None.
        start_position (int): Posición incial de memoria. Defaults to 0.
        end_position (int): Posición final de memoria 
    """
    def __init__(self, space, process = None) -> None:
        """Constructor de la clase. Genera el espacio de memoria, en caso de que sea necesario, 
        se le puede añadir un proceso durante la construcción

        Args:
            space (int): Espacio que ocupa el proceso
            process (Process, optional): Proceso que tendrá el espacio de memoria. Defaults to None.
        """
        self.process = process
        self.space = space
        self.end_position = space-1
        self.start_position = 0
    
    def __str__(self) -> str:
        """Método que devuelve una cadena de texto descriptivo del espacio de memoria

        Returns:
            str: una cadena de texto descriptivo del espacio de memoria
        """
        return f"Position:{self.start_position}-{self.end_position}, Process:[{self.process}]"

    def insertProcess(self, process: Process):
        """Método que inserta un proceso y genera el fragmento necesario para contenerlo a partir de este.

        Args:
            process (Process): Proceso a añadir

        Raises:
            InsuficientFragmentSpaceError: En caso de que el proceso ocupe más memoria que este fragmento

        Returns:
            PageSpace: Un fragmento de memoria vacío con la memoria restante después de añadir el proceso
        """
        if process.memory > self.space:
            raise InsuficientFragmentSpaceError()
        self.process = process
        fragment = PageSpace(self.space - process.memory, None)
        fragment.start_position = self.start_position + process.memory
        fragment.end_position = self.end_position
        self.end_position = process.memory + self.start_position -1
        self.resize(process.memory)
        return fragment

    def resize(self, space):
        """Método para cambiar el tamaño del fragmento de memoria

        Args:
            space (int): Nuevo espacio que tendrá el fragmento
        """
        self.space = space


class NoMoreSpaceError(Exception): #excepcion
    """Error que ocurre cuando no hay más espacio en la memoria
    """
    def __init__(self) -> None:
        super().__init__("No more space remaining")
        
class ISorting(ABC): #clase abstracta
    """Clase abstracta que representa los métodos de uso de memoria, o Mejor Hueco o Peor Hueco.
    Nota: Hereda la clase ABC que indica que la clase es abstracta
    """
    @abstractmethod
    def searchPage(self, pageList, processSize):
        """Método de busqueda del Mejor Hueco o Peor Hueco para el proceso que viene

        Args:
            pageList (list): Lista de procesos
            processSize (int): Tamaño del proceso
            
        Raises:
            InsuficientFragmentSpaceError: En caso de que el proceso ocupe más memoria que este fragmento
            
        Returns:
            int: Índice del fragmento que se adecue al método
        """
        pass #abstract

class BestFitSorting(ISorting):
    """Clase que representa el método de Mejor Hueco
    """
    def searchPage(self, pageList: list, processSize):
        emptySpaces = [page for page in pageList if page.process is None]
        if min(emptySpaces, key=lambda page: page.space).space < processSize:
            raise InsuficientFragmentSpaceError()
        if len(pageList) == 1:
            return 0
        bestSize = 0
        copypages = pageList.copy()
        copypages.sort(key=lambda p: p.space)
        for i, page in enumerate(copypages):
            if page.process is not None:
                continue
            if processSize <= page.space:
                bestSize = pageList.index(copypages[i])
        return bestSize

class WorstFitSorting(ISorting):
    """Clase que representa el método de Peor Hueco
    """
    def searchPage(self, pageList: list, processSize):
        emptySpaces = [page for page in pageList if page.process is None]
        if min(emptySpaces, key=lambda page: page.space).space < processSize:
            raise InsuficientFragmentSpaceError()
        if len(pageList) == 1:
            return 0
        bestSize = 0
        copypages = sorted(pageList, key=lambda p: p.space, reverse=True)
        for i, page in enumerate(copypages):
            if page.process is not None:
                continue
            if processSize <= page.space:
                bestSize = pageList.index(copypages[i])
        return bestSize

class ProcessLine:
    """Clase que representa la línea de procesos, esta clase contiene métodos para gestionar la memoria de manera eficiente según el método
    que se le indique 

    Attributes:
        DEFAULT_SIZE (int): Tamaño por defecto de la memoria
        processList (list): Lista de procesos de la memoria
        __time__ (int): Instante de tiempo en el que se encuentra la línea. Defaults to 1
        __buff__ (ProcessBuffer): Buffer de procesos donde se hayan los procesos que no han podido ser añadidos por primera vez
        sorting (ISorting): Método de busqueda del Mejor/Peor hueco
        size (int): Tamaño de la línea de procesos
    """
    DEFAULT_SIZE = 2000 #memory defaultspace

    def __init__(self, sorting: ISorting, size = DEFAULT_SIZE):
        """Constructor de la clase genera la lista vacía con un buffer de espera y determina el método de busqueda de huecos.

        Args:
            sorting (ISorting): Método de búsqueda de huecos a usar
            size (int, optional): Tamaño máximo de memoria. Defaults to DEFAULT_SIZE.
        """
        f = open("result.txt", "w").close() #limpiar archivo resultado
        self.size = size
        self.__buff__ = ProcessBuffer()
        self.processList = []
        self.processList.append(PageSpace(size))
        self.sorting = sorting
        self.__time__ = 1
        

    def insertProcess(self, process: Process):
        """Método para introducir procesos a la memoria. Busca entre todos los huecos el que más se adecue según el método empleado.
        Añade el proceso a un buffer secundario en caso de que no se pueda añadir.

        Args:
            process (Process): Proceso a añadir

        Raises:
            err (InsuficientFragmentSpaceError): Error en caso de que no haya fragmento adecuado para introducir el proceso 
        """
        if process is None:
            return
        if process.memory > self.size:
            raise NoMoreSpaceError()
        try:
            index = self.sorting.searchPage(self.processList, process.memory)
            page = self.processList[index].insertProcess(process)
            self.processList.append(page)
            print("Joining:", process, "in space:", self.processList[index])
        except InsuficientFragmentSpaceError as err:
            print("Process:", process, err)
            self.__buff__.addToBuffer(process)
            raise err

    def insertProcesses(self, processes: list):
        """Método para añadir varios procesos a la linea de procesos.

        Args:
            processes (list): Lista de procesos a añadir.
        """
        for process in processes:
            try:
                self.insertProcess(process)
            except InsuficientFragmentSpaceError as err:
                continue
            except NoMoreSpaceError as err:
                print("Process:", process, err)
                continue

    def update(self, processes: list = []):
        """Método que gestiona lo que ocurre en memoria cuando se pasa al siguiente intervalo.
        Escribe en el archivo de salida "result.txt" informando de los cambios

        Args:
            processes (list, optional): Lista de procesos a añadir durante la ejecución. Defaults to [].
        """
        print(f"{self.__time__} -> {self.__time__+1}")
        f = open("result.txt", "a")
        f.write(f"{self.__time__}")
        if len(processes) != 0:
            self.insertProcesses(processes)
        if len(self.__buff__.processList) != 0:
            for _ in range(len(self.__buff__.processList)):
                self.insertProcesses([self.__buff__.getNextProcess(self.getMaxPageSize())])
        for process in self.processList:
            if process.process is None:
                if process.start_position != self.size or process.space == self.size:
                    f.write(f" [{process.start_position} hueco {process.space}]")
                continue
            f.write(f" [{process.start_position} {process.process.name} {process.space}]")
            process.process.execTime -= 1
            if process.process.execTime <= 0:
                print("Leaving:", process.process)
                process.process = None
        self.__time__ += 1
        self.recalculateSpace()
        print("-------------------")
        f.write("\n")
        f.close()

    def __str__(self) -> str:
        retstr = "List of process:\n"
        for process in self.processList:
            retstr += process + '\n'
        return retstr

    def recalculateSpace(self):
        """Método para recalcular el espacio en caso de haber dos (o más) huecos vacíos consecutivos y 
        ordenar los fragmentos dentro de la memoria por posición inicial.
        """
        i = 0
        while i < len(self.processList) - 1:
            current_page = self.processList[i]
            next_page = self.processList[i + 1]
            if current_page.process is None and next_page.process is None:
                current_page.resize(current_page.space + next_page.space)
                current_page.end_position = next_page.end_position
                del self.processList[i + 1]
            else:
                i += 1  # Solo avanzamos si no se han combinado los fragmentos
        self.processList.sort(key=lambda p: p.start_position) # Ordenar los fragmentos por posición incial

    def getMaxPageSize(self):
        """Obtiene el espacio más grande de memoria dentro de la lista

        Returns:
            int: Tamaño del fragmento más grande
        """
        bigger = -1
        for page in self.processList:
            if bigger < page.space:
                bigger = page.space
        return bigger

def getProcessesToAdd(processes, time):
    """Obtiene los procesos a añadir en el tiempo dado. A la vez los saca de la lista de procesos.

    Args:
        processes (list): Lista de todos los procesos que van a ser añadidos
        time (int): Instante de tiempo actual

    Returns:
        list: Lista de procesos que se pueden añadir en el intervalo dado 
    """
    ready_processes = [process for process in processes if process.arribal == time]
    processes[:] = [process for process in processes if process.arribal != time]
    return ready_processes

def generateProcessFromFile(filename = "samples/process.txt"):
    """Genera la lista de procesos según el archivo dado

    Args:
        filename (str, optional): Nombre del archivo para cargar los datos. Defaults to "samples/process.txt".

    Returns:
        list: Lista de procesos del archivo
    """
    processes = []
    f = open(filename, 'r')
    for line in f:
        data = line.split(" ")
        processes.append(Process(data[0], int(data[1]), int(data[2]), int(data[3])))
    f.close()
    return processes

if __name__ == '__main__':
    print("Elige metodo:", "1) Peor hueco", "2) Mejor Hueco", "q) Salir", sep='\n')
    answ = input()
    if answ == '1':
        line = ProcessLine(WorstFitSorting())
    elif answ == '2':
        line = ProcessLine(BestFitSorting())
    else:
        exit(0)
    try:
        processes = generateProcessFromFile(sys.argv[1])
    except:
        processes = generateProcessFromFile()
    while len(processes) != 0 or len(line.__buff__.processList) != 0 or not all(ps.process is None for ps in line.processList):
        line.update(processes=getProcessesToAdd(processes, line.__time__))
        time.sleep(1)

