from flask import Flask, json, send_file
import sys
sys.path.append('../../boards')
from board import Board

boardname = "zlagboard_evo" # FIXME: config
a = Board(boardname=boardname,basedir="../../boards/")

api = Flask(__name__)

@api.route('/', methods=['GET'])
def root():
  get_board() 
  return json.dumps(a.boardname_full)

@api.route('/board', methods=['GET']) # FIXME: API doc
def get_board():
  return json.dumps(a.boardname_full)

@api.route('/board/data', methods=['GET'])
def get_board_data():
  return json.dumps(a.boarddata)

@api.route('/board/get_hold_for_type/<type>', methods=['GET'])
def get_hold_for_type(type):
  return json.dumps(a.get_hold_for_type(type))

@api.route('/board/img/<left>/<right>', methods=['GET']) # FIXME generate all images in advance
def get_img_left_right(left,right):
  fname = a._cache_png_filename(left,right)
  return send_file(fname, mimetype='image/png')

@api.route('/board/img', methods=['GET']) # FIXME: slashes safe?
def get_img():
  fname = a.boardimagename_png
  return send_file(fname, mimetype='image/png')

if __name__ == '__main__':
    api.run() 
