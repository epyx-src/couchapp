// from couch.js

CouchApp.path = {
  encodeOptions: function(options, noJson) {
    var buf = [];
    if (typeof(options) == "object" && options !== null) {
      for (var name in options) {
        if (!options.hasOwnProperty(name)) continue;
        var value = options[name];
        if (!noJson && (name == "key" || name == "startkey" || name == "endkey")) {
          value = toJSON(value);
        }
        buf.push(encodeURIComponent(name) + "=" + encodeURIComponent(value));
      }
    }
    if (!buf.length) {
      return "";
    }
    return "?" + buf.join("&");
  },

  concatArgs: function(array, args) {
    for (var i=0; i < args.length; i++) {
      array.push(args[i]);
    };
    return array;
  },

  makePath: function(array) {
    var options, path;

    if (typeof array[array.length - 1] != "string") {
      // it's a params hash
      options = array.pop();
    };
    path = array.map(function(item) {return encodeURIComponent(item);}).join('/');
    if (options) {
      return path + this.encodeOptions(options);
    } else {
      return path;    
    }
  },

  assetPath: function() {
    var p = req.path, parts = ['', p[0], p[1] , p[2]];
    return this.makePath(this.concatArgs(parts, arguments));
  },

  showPath: function() {
    var p = req.path, parts = ['', p[0], p[1] , p[2], '_show'];
    return this.makePath(this.concatArgs(parts, arguments));
  },

  updatePath: function() {
    var p = req.path, parts = ['', p[0], p[1] , p[2], '_update'];
    return this.makePath(this.concatArgs(parts, arguments));
  },

  listPath: function() {
    var p = req.path, parts = ['', p[0], p[1] , p[2], '_list'];
    return this.makePath(this.concatArgs(parts, arguments));
  },

  olderPath: function(info) {
    if (!info) return null;
    var q = req.query;
    q.startkey = info.prev_key;
    q.skip=1;
    return this.listPath('index','recent-posts',q);
  },

  makeAbsolute: function(req, path) {
    return 'http://' + req.headers.Host + path;
  },

  currentPath: function() {
    path = req.path.map(function(item) {return encodeURIComponent(item);}).join('/');
    if (req.query) {
      return path + this.encodeOptions(req.query, true);
    } else {
      return path;
    }
  }
};