
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftPLUSMINUSleftTIMESDIVIDEleftPOWERrightUMINUSCOMMA CONST DIVIDE ID LPAREN MINUS NUMBER PLUS POWER RPAREN TIMESstatement : expressionexpression : IDexpression : MINUS expression %prec UMINUSexpression : expression PLUS expression\n                    | expression MINUS expression\n                    | expression TIMES expression\n                    | expression DIVIDE expression\n                    | expression POWER NUMBERexpression : LPAREN expression RPARENexpression : NUMBERexpression : CONSTexpression : ID LPAREN arguments RPARENexpression : TIMES TIMES ID LPAREN arguments RPARENarguments : argumentarguments : arguments COMMA argumentargument : expression'
    
_lr_action_items = {'ID':([0,4,7,9,10,11,12,14,16,29,30,],[3,3,3,3,3,3,3,3,26,3,3,]),'MINUS':([0,2,3,4,6,7,8,9,10,11,12,14,15,17,18,19,20,21,22,25,27,28,29,30,33,],[4,10,-2,4,-10,4,-11,4,4,4,4,4,-3,10,-4,-5,-6,-7,-8,10,-9,-12,4,4,-13,]),'LPAREN':([0,3,4,7,9,10,11,12,14,26,29,30,],[7,14,7,7,7,7,7,7,7,30,7,7,]),'NUMBER':([0,4,7,9,10,11,12,13,14,29,30,],[6,6,6,6,6,6,6,22,6,6,6,]),'CONST':([0,4,7,9,10,11,12,14,29,30,],[8,8,8,8,8,8,8,8,8,8,]),'TIMES':([0,2,3,4,5,6,7,8,9,10,11,12,14,15,17,18,19,20,21,22,25,27,28,29,30,33,],[5,11,-2,5,16,-10,5,-11,5,5,5,5,5,-3,11,11,11,-6,-7,-8,11,-9,-12,5,5,-13,]),'$end':([1,2,3,6,8,15,18,19,20,21,22,27,28,33,],[0,-1,-2,-10,-11,-3,-4,-5,-6,-7,-8,-9,-12,-13,]),'PLUS':([2,3,6,8,15,17,18,19,20,21,22,25,27,28,33,],[9,-2,-10,-11,-3,9,-4,-5,-6,-7,-8,9,-9,-12,-13,]),'DIVIDE':([2,3,6,8,15,17,18,19,20,21,22,25,27,28,33,],[12,-2,-10,-11,-3,12,12,12,-6,-7,-8,12,-9,-12,-13,]),'POWER':([2,3,6,8,15,17,18,19,20,21,22,25,27,28,33,],[13,-2,-10,-11,-3,13,13,13,13,13,-8,13,-9,-12,-13,]),'RPAREN':([3,6,8,15,17,18,19,20,21,22,23,24,25,27,28,31,32,33,],[-2,-10,-11,-3,27,-4,-5,-6,-7,-8,28,-14,-16,-9,-12,-15,33,-13,]),'COMMA':([3,6,8,15,18,19,20,21,22,23,24,25,27,28,31,32,33,],[-2,-10,-11,-3,-4,-5,-6,-7,-8,29,-14,-16,-9,-12,-15,29,-13,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statement':([0,],[1,]),'expression':([0,4,7,9,10,11,12,14,29,30,],[2,15,17,18,19,20,21,25,25,25,]),'arguments':([14,30,],[23,32,]),'argument':([14,29,30,],[24,31,24,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> statement","S'",1,None,None,None),
  ('statement -> expression','statement',1,'p_statement_expr','parser.py',78),
  ('expression -> ID','expression',1,'p_expression_variable','parser.py',82),
  ('expression -> MINUS expression','expression',2,'p_expression_uop','parser.py',90),
  ('expression -> expression PLUS expression','expression',3,'p_expression_binop','parser.py',94),
  ('expression -> expression MINUS expression','expression',3,'p_expression_binop','parser.py',95),
  ('expression -> expression TIMES expression','expression',3,'p_expression_binop','parser.py',96),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_binop','parser.py',97),
  ('expression -> expression POWER NUMBER','expression',3,'p_expression_binop','parser.py',98),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','parser.py',111),
  ('expression -> NUMBER','expression',1,'p_expression_number','parser.py',115),
  ('expression -> CONST','expression',1,'p_expression_const','parser.py',119),
  ('expression -> ID LPAREN arguments RPAREN','expression',4,'p_expression_function','parser.py',123),
  ('expression -> TIMES TIMES ID LPAREN arguments RPAREN','expression',6,'p_expression_alldepths','parser.py',132),
  ('arguments -> argument','arguments',1,'p_arguments','parser.py',143),
  ('arguments -> arguments COMMA argument','arguments',3,'p_arguments_1','parser.py',147),
  ('argument -> expression','argument',1,'p_argument','parser.py',152),
]
