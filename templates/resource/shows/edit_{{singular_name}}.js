function(doc, req) {
  // !code vendor/mustache.js
  // !code vendor/couchapp/couchapp.js
  // !code vendor/couchapp/rendering.js
  // !code vendor/couchapp/date.js
  // !code vendor/couchapp/path.js
  // !json templates.{{singular_name}}s.edit
  // !json templates.layout
  
  return CouchApp.rendering.render_template(doc, templates, templates.{{singular_name}}s.edit, {
    {{singular_name}}: [doc],
    id: doc['_id'],
    show_url: CouchApp.path.showPath('{{singular_name}}', doc['_id']),
    update_url: CouchApp.path.updatePath('{{singular_name}}', doc['_id'])
  });
}
