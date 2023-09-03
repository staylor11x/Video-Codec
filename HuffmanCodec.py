from Node import Node


class HuffmanCodec:

    def __init__(self):

        self.symbol_with_probs = dict()
        self.codes = dict()
        self.nodes = []
        self.encoding_output = []
        self.encoded_output = ''


    def calculate_probability(self):
        for element in self.data:
            if self.symbol_with_probs.get(element) == None:
                self.symbol_with_probs[element] = 1
            else:
                self.symbol_with_probs[element] += 1
   
    def calculate_codes(self, node, val=''):
        newVal = val + str(node.code)
        if(node.left):
            self.calculate_codes(node.left, newVal)
        if(node.right):
            self.calculate_codes(node.right, newVal)
        if(not node.left and not node.right):
            self.codes[node.symbol] = newVal

    def output_encoded(self):
        for c in self.data:
            self.encoding_output.append(self.codes[c])
        
        self.encoded_output = ''.join([str(item) for item in self.encoding_output])
    
    def huffman_encoding(self, data):

        self.data = data

        self.calculate_probability()
        symbols = self.symbol_with_probs.keys()
        probabilities = self.symbol_with_probs.values()
        print("Symbols: ", symbols)
        print("probabilities: ", probabilities)

        for symbol in self.symbol_with_probs:
            self.nodes.append(Node(self.symbol_with_probs.get(symbol), symbol))

        while len(self.nodes) > 1:
            self.nodes = sorted(self.nodes, key=lambda x:x.prob)

            right = self.nodes[0]
            left = self.nodes[1]

            left.code = 0
            right.code = 1

            newNode = Node(left.prob+right.prob, left.symbol+right.symbol, left, right)

            self.nodes.remove(left)
            self.nodes.remove(right)
            self.nodes.append(newNode)

        self.calculate_codes(self.nodes[0])
        self.output_encoded()

        return self.encoded_output, self.nodes[0]
    
    @staticmethod
    def huffman_decoding(encoded_data, huffman_tree):
        tree_head = huffman_tree
        decoded_output = []

        for x in encoded_data:
            if x == '1':
                huffman_tree = huffman_tree.right
            elif x == '0':
                huffman_tree = huffman_tree.left
            try:
                if huffman_tree.left.symbol == None and huffman_tree.right.symbol == None:
                    pass
            except AttributeError:
                decoded_output.append(huffman_tree.symbol)
                huffman_tree = tree_head

        string = ''.join([str(item) for item in decoded_output])
        return string

    @staticmethod
    def _find_first_difference(str1, str2):
        '''Check to see if the strings decoded and encoded are the same'''
        min_len = min(len(str1), len(str2))

        for i in range(min_len):
            if str1[i] != str2[i]:
                return False

        # If the strings have different lengths, return the length of the shorter string
        if len(str1) != len(str2):
            return False

        # If the strings are identical, return true
        return True
    
