from telnetlib import ENCRYPT
from flask import Flask, jsonify, request,Response
from neo4j import GraphDatabase, basic_auth
from flask_cors import CORS
import json
from neo4j import GraphDatabase
from py2neo import Graph
from py2neo import Subgraph
import py2neo
""" config.py
// Adding config file to config your local data folder please !!!!!!!!!!!

// e.g.
localfile_path = "../../../local_data"
"""
from config import localfile_path
from helper import filterGraph, print_, get_subgraph, convert_subgraph_to_json,graph_after_delete_node, graph_after_expand_node
# configuration
DEBUG = True
GRAPH_DRIVER = None
# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# graph = None 

# entity_identifier = None
# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/getGraphData', methods=['GET'])
def getGraphData():
    f = open(f'{localfile_path}/input_graph.json')
    # f = open('../../../local_data/graph.json')
    data = json.load(f)
    # print(type(filtered_data))
    return Response(json.dumps(data))

@app.route('/getTableData', methods=['GET'])
def getTableData():
    ## Create a new py file config.py and add localfile_path to indicate the place of local_data folder
    ## This config file will not be pushed to the osu code, so we don't need to always change path
    # f = open('../../../local_data/cfs_relation_table.json')
    f = open(f'{localfile_path}/ppod_table.json')
    data = json.load(f)
    output = {} ## tableName: {tableData:{}, tableInfo:{}}
    tableNames = []
    for ele in data:
        tableNames.append(ele['table_name'])
        output[ele['table_name']] = {
            'tableData': ele['table_data'],
            'tableInfo': ele['table_info']
        }
    result = {
        'data': output,
        'sheet': tableNames
    }
    # data = data.fillna('')
    # print(data.columns)

    # dados = data.to_dict('records')
    # output = {
    #     'data': dados,
    # }
    # print(data.keys())
    return Response(json.dumps(result))

@app.route('/retrieveSubgraph', methods=['POST'])
def getSubGraphFromTable(): 
    request_obj = request.get_json()
    nodes_list = []
    relation_list = []
    if request_obj.get("nodes") is not None: 
        nodes_list = request_obj.get("nodes")
    
    if request_obj.get("relations") is not None:
        relation_list = request_obj.get("relations")
    subgraph_res = get_subgraph(graph, nodes_list, relation_list)
    dict_res = convert_subgraph_to_json(subgraph_res, entity_identifier)
    return Response(json.dumps(dict_res))

@app.route('/deleteNode', methods=['POST'])
def delete_node_from_graph():
    request_obj = request.get_json()
    nodes_list = []
    relation_list = []
    if request_obj.get("nodes") is not None:
        nodes_list = request_obj.get("nodes")
    if request_obj.get("relations") is not None:
        relation_list = request_obj.get("relations")
    if request_obj.get("delete_node") is not None:
        delete_node = request_obj.get("delete_node")
    subgraph_res = graph_after_delete_node(nodes_list,relation_list,delete_node,graph)
    dict_res = convert_subgraph_to_json(subgraph_res, entity_identifier)
    return Response(json.dumps(dict_res))

@app.route('/expandNode', methods=['POST'])
def expand_node_from_graph():
    request_obj = request.get_json()
    print(request_obj)
    nodes_list = []
    relation_list = []
    limit_number = 5
    if request_obj.get("nodes") is not None:
        nodes_list = request_obj.get("nodes")
    if request_obj.get("relations") is not None:
        relation_list = request_obj.get("relations")
    if request_obj.get("expand_node") is not None:
        expand_node = request_obj.get("expand_node")
    if request_obj.get("limit_number") is not None:
        limit_number = request_obj.get("limit_number")
    subgraph_res = graph_after_expand_node(graph,nodes_list,relation_list,expand_node,limit_number)
    dict_res = convert_subgraph_to_json(subgraph_res, entity_identifier)
    return Response(json.dumps(dict_res))

if __name__ == '__main__':
    
    global graph, entity_identifier
    # driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123"))
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "123")) # This should be a global variable in this app
    schema = py2neo.database.Schema(graph)
    if len(list(schema.node_labels)) > 1:
        entity_identifier = "label" # This should be a global variable in this app
    else:
        entity_identifier = "county" # This should be a global variable in this app
    app.run()
