"""Python AST parser. Emits structural facts, never source snippets."""
import ast, hashlib
def parse_python(source):
    tree=ast.parse(source); functions=[]; classes=[]; imports=[]; flow=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            params=[a.arg for a in node.args.posonlyargs+node.args.args+node.args.kwonlyargs]
            functions.append({"name":node.name,"kind":"async" if isinstance(node,ast.AsyncFunctionDef) else "function","parameters":params,"line":node.lineno,"returns_annotation_present":node.returns is not None})
            flow.append({"operation":node.name,"control_constructs":sorted({type(n).__name__ for n in ast.walk(node) if isinstance(n,(ast.If,ast.For,ast.AsyncFor,ast.While,ast.Try,ast.Match))})})
        elif isinstance(node,ast.ClassDef): classes.append({"name":node.name,"line":node.lineno,"bases_count":len(node.bases)})
        elif isinstance(node,(ast.Import,ast.ImportFrom)): imports.extend(a.name for a in node.names)
    return {"artifact_type":"code","facts":{"language":"python","source_sha256":hashlib.sha256(source.encode()).hexdigest(),"functions":functions,"classes":classes,"dependencies":sorted(set(imports)),"control_flow":flow,"source_text_retained":False},"warnings":["Static AST analysis does not prove runtime behavior or full semantic equivalence."]}
