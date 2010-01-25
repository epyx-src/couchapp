// taken from http://github.com/quirkey/sammy/blob/master/lib/plugins/sammy.nested_params.js

CouchApp.params = {
  parseNestedParams: function(original_params) {
    var params = {};
    for(var name in original_params) {
      params = this.parseNestedParam(original_params[name], name, params);
    }
    return params;
  },

  parseNestedParam: function(field_value, field_name, params) {
    var match, name, rest;

    if (field_name.match(/^[^\[]+$/)) {
      // basic value
      params[field_name] = unescape(field_value);
    } else if(match = field_name.match(/^([^\[]+)\[\](.*)$/)) {
      // array
      name = match[1];
      rest = match[2];

      if(params[name] && !isArray(params[name])) { throw('400 Bad Request'); }

      if (rest) {
        // array is not at the end of the parameter string
        match = rest.match(/^\[([^\]]+)\](.*)$/);
        if(!match) { throw('400 Bad Request'); }

        if (params[name]) {
          if(params[name][params[name].length - 1][match[1]]) {
            params[name].push(this.parseNestedParam(field_value, match[1] + match[2], {}));  
          } else {
            this.extend(params[name][params[name].length - 1], this.parseNestedParam(field_value, match[1] + match[2], {}));  
          }            
        } else {
          params[name] = [this.parseNestedParam(field_value, match[1] + match[2], {})];
        }                    
      } else {
        // array is at the end of the parameter string
        if (params[name]) {
          params[name].push(unescape(field_value));
        } else {
          params[name] = [unescape(field_value)];
        }          
      }
    } else if (match = field_name.match(/^([^\[]+)\[([^\[]+)\](.*)$/)) {
      // hash
      name = match[1];
      rest = match[2] + match[3];

      if (params[name] && isArray(params[name])) { throw('400 Bad Request'); }

      if (params[name]) {          
        this.extend(params[name], this.parseNestedParam(field_value, rest, params[name]));
      } else {
        params[name] = this.parseNestedParam(field_value, rest, {});
      }
    }
    return params;

    function isArray(obj) {
      return obj.constructor == Array;
    }
  },

  extend: function(hash1, hash2) {
    for(var name in hash2) {
      hash1[name] = hash2[name];
    };
    return hash1;
  }
};

