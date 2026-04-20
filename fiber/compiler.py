import pickle
import zlib
from .ast_nodes import Program

MAGIC = b"\x46\x49\x42\x02"  # "FIB\x02"

def compile_to_binary(ast_node: Program) -> bytes:
    """Serializes a Program AST to a compressed binary format."""
    # We use pickle to serialize the AST nodes as they are pure data containers
    data = pickle.dumps(ast_node)
    compressed = zlib.compress(data)
    return MAGIC + compressed

def load_from_binary(binary_data: bytes) -> Program:
    """Deserializes a Program AST from binary data."""
    if not binary_data.startswith(MAGIC):
        raise ValueError("Invalid Fiber binary file (Magic mismatch)")
    
    compressed = binary_data[len(MAGIC):]
    data = zlib.decompress(compressed)
    ast = pickle.loads(data)
    
    if not isinstance(ast, Program):
        raise ValueError("Malformed Fiber binary: Root node is not a Program")
        
    return ast
