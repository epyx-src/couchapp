function(doc, req) {
  // !code vendor/math.uuid.js
  // !code vendor/mustache.js
  // !code vendor/couchapp/couchapp.js
  // !code vendor/couchapp/date.js
  // !code vendor/couchapp/path.js
  // !code vendor/couchapp/params.js
  // !json templates.{{plural_name}}.create
    
  if(!doc) {
    doc = {
      '_id': Math.uuid(),
      'type': '{{singular_name}}',
      'created_at': new Date().toJSON()
    };
  };
  
  
  nested_params = CouchApp.params.parseNestedParams(req.form);
  CouchApp.params.extend(doc, nested_params['{{singular_name}}']);
  
  if(doc._deleted == "true") { doc._deleted = true; }
  
  var url = doc._deleted ? CouchApp.path.listPath('{{plural_name}}', '{{plural_name}}') : CouchApp.path.showPath('{{singular_name}}', doc['_id']);
  return [doc, Mustache.to_html(templates.{{plural_name}}.create, {'url': url})];
}