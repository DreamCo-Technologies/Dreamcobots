"""Optional Tree-sitter adapter for supported source languages."""
def parse_tree_sitter(source, language):
    try:
        from tree_sitter_language_pack import get_parser
    except ImportError as exc:
        raise RuntimeError("Install requirements-reverse-engineer.txt to enable Tree-sitter parsing.") from exc
    parser=get_parser(language)
    tree=parser.parse(source.encode("utf-8"))
    if tree.root_node.has_error:
        raise ValueError("Tree-sitter found syntax errors; refusing partial extraction.")
    function_types={"function_declaration","function_definition","function_item","method_declaration","method_definition","constructor_declaration","arrow_function"}
    import_types={"import_statement","import_declaration","use_declaration","package_clause","preproc_include","include_directive"}
    control_types={"if_statement","for_statement","while_statement","switch_statement","try_statement","match_expression","loop_expression","do_statement","preproc_if","preproc_ifdef"}
    class_types={"class_specifier","struct_specifier","class_declaration","interface_declaration","enum_specifier"}
    identifier_types={"identifier","field_identifier","type_identifier","qualified_identifier","operator_name","destructor_name"}
    def find_identifier(node):
        if node is None:
            return None
        stack=[node]
        while stack:
            current=stack.pop()
            if current.type in identifier_types:
                return current.text.decode("utf-8",errors="replace")
            stack.extend(reversed(current.named_children))
        return None
    functions=[]; classes=[]; imports=set(); flow=[]; nodes=[tree.root_node]
    while nodes:
        node=nodes.pop()
        if node.type in function_types:
            name_node=node.child_by_field_name("name")
            if name_node is None:
                name_node=node.child_by_field_name("declarator")
            params=node.child_by_field_name("parameters")
            name=find_identifier(name_node) or "anonymous"
            functions.append({"name":name,"kind":"function","parameters":[],"parameter_node_count":len(params.named_children) if params else None,"line":node.start_point.row+1,"returns_annotation_present":node.child_by_field_name("return_type") is not None})
        if node.type in class_types:
            class_name=find_identifier(node.child_by_field_name("name")) or find_identifier(node)
            if class_name: classes.append({"name":class_name,"line":node.start_point.row+1,"kind":node.type})
        if node.type in import_types:
            path_node=node.child_by_field_name("path") or node.child_by_field_name("source")
            imports.add(path_node.text.decode("utf-8",errors="replace") if path_node else node.type)
        if node.type in control_types:flow.append({"operation":"control_flow","control_constructs":[node.type],"line":node.start_point.row+1})
        nodes.extend(reversed(node.children))
    return {"artifact_type":"code","facts":{"language":language,"functions":functions,"classes":classes,"dependencies":sorted(imports),"control_flow":flow,"source_text_retained":False},"warnings":["Tree-sitter output is syntax structure only; dynamic behavior and dependency resolution are not inferred."]}
