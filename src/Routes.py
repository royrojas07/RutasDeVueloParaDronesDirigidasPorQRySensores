class Routes:
    def __init__(self, matrix):
        self.saved_routes = open("Routes_file.txt", "a+")
        self.routes_amount = 0
        self.read_file(matrix)

    def read_file(self, matrix): #matrix es una lista de listas
        #saved_routes = open("Routes_file","a")
        self.saved_routes.seek(0)
        routes = self.saved_routes.readlines()
        matrix.clear()
        for route in routes:
            instructions = route.split("\t")
            self.routes_amount += 1
            matrix.append(instructions)

    def write_route(self, route):
        self.saved_routes.write(route + "\n")

    def close_file(self):
        self.saved_routes.close()
