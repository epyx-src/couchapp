var test_<%plural_name%> = new function() {
  this.delete_objects = function() {
    var db = new CouchDB(this.db);
    db.allDocs()['rows'].forEach(function(row) {
      if(!row['id'].match(/^_design/)) {
        db.deleteDoc({'_id': row['id'], '_rev': row['value']['rev']});
      };
    });
  };
  
  this.setup = function() {
    this.db = '<%singular_name%>_test';
    this.admin = '';
    this.password = '';
    this.delete_objects();
  };
  
  var app_url = 'http://localhost:5984/<%singular_name%>_test/_design/<%singular_name%>/';
  
  this.test_create_<%singular_name%> = to_test([
    ['open', {url: app_url + "<%plural_name%>/new.html"}],
    <%#attributes%>
        ['type', {text: "test_<%name%>", id: "<%singular_name%>_<%name%>"}],
    <%/attributes%>
    ['click', {value: "Create"}],
    <%#attributes%>
        ['asserts.assertText', {xpath: "//p[@class='<%class%>']", validator: "<%label%>: test_<%name%>"}],
    <%/attributes%>
  ]);
  
  <%#first_attribute%>
  this.test_list_<%plural_name%> = to_test(create_<%singular_name%>({<%name%>: 'test_<%name%>'}).concat([
    ['open', {url: app_url + "_list/<%plural_name%>/<%plural_name%>?descending=true"}],
    ['asserts.assertText', {xpath: "//p[@class='<%class%>']", validator: '<%label%>: test_<%name%>'}],
    ['click', {link: 'Show'}],
    ['asserts.assertText', {xpath: "//p[@class='<%class%>']", validator: '<%label%>: test_<%name%>'}]
  ]));

  this.test_delete_<%singular_name%> = to_test(create_<%singular_name%>({<%name%>: 'test_<%name%>'}).concat([
    ['open', {url: app_url + "_list/<%plural_name%>/<%plural_name%>?descending=true"}],
    ['asserts.assertText', {xpath: "//p[@class='<%class%>']", validator: '<%label%>: test_<%name%>'}],
    ['click', {link: 'Show'}],
    ['click', {value: 'Remove'}],
    ['asserts.assertNotText', {xpath: "//p[@class='<%class%>']", validator: '<%label%>: test_<%name%>'}]
  ]));
  
  this.test_edit_<%singular_name%> = to_test(create_<%singular_name%>({<%name%>: 'test_<%name%>'}).concat([
    ['open', {url: app_url + "_list/<%plural_name%>/<%plural_name%>?descending=true"}],
    ['click', {link: 'Show'}],
    ['click', {link: 'Edit'}],
    ['type', {text: "test2_<%name%>", id: "<%singular_name%>_<%name%>"}],
    ['click', {value: "Save"}],
    ['asserts.assertText', {xpath: "//p[@class='<%class%>']", validator: '<%label%>: test2_<%name%>'}]
  ]));
  <%/first_attribute%>
  
  // --------------------------------
  
  function create_<%singular_name%>(options) {
    options = options || {};
    return [
      ["open", {url: app_url + "<%plural_name%>/new.html"}],
      <%#attributes%>
        ["type", {text: options.<%name%> || "test_<%name%>", id: "<%singular_name%>_<%name%>"}],
      <%/attributes%>
      ["click", {value: "Create"}]
    ]; 
  };
  
  function to_test(arrays) {
    return arrays.map(function(array) {
      return {method: array[0], params: array[1]};
    });
  };
};