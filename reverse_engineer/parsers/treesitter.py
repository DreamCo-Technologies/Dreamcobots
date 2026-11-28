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
    import_types={"import_statement","import_declaration","use_declaration","package_clause"}
    control_types={"if_statement","for_statement","while_statement","switch_statement","try_statement","match_expression","loop_expression"}
    functions=[]; imports=set(); flow=[]; nodes=[tree.root_node]
    while nodes:
        node=nodes.pop()
        if node.type in function_types:
            name_node=node.child_by_field_name("name")
            params=node.child_by_field_name("parameters")
            name=name_node.text.decode("utf-8",errors="replace") if name_node else "anonymous"
            functions.append({"name":name,"kind":"function","parameters":[],"parameter_node_count":len(params.named_children) if params else None,"line":node.start_point.row+1,"returns_annotation_present":node.child_by_field_name("return_type") is not None})
        if node.type in import_types:imports.add(node.type)
        if node.type in control_types:flow.append({"operation":"control_flow","control_constructs":[node.type],"line":node.start_point.row+1})
        nodes.extend(reversed(node.children))
    return {"artifact_type":"code","facts":{"language":language,"functions":functions,"classes":[],"dependencies":sorted(imports),"control_flow":flow,"source_text_retained":False},"warnings":["Tree-sitter output is syntax structure only; dynamic behavior and dependency resolution are not inferred."]}
