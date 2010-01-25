// register assertNotText
windmill.controller.asserts.assertNotText = function (paramObject) {
  var n;
  try {
    n = lookupNode(paramObject, false);
  } catch(e) {
    if(e.match(/failed/)) {
      return true;
    } else {
      throw e;
    };
  }
  var validator = paramObject.validator;
  
  var inner = n.innerHTML;
  if (n.textContent){
    inner = n.textContent;
  } else if (n.innerText) {
    inner = n.innerText;
  }
  
  var iHTML = inner.replace(/^\s*|\s*$/g,'');
  if (iHTML != validator){
    return true;
  }
  
  throw "Text '" + validator +
        "' was found in the provided node.  Found instead: " + iHTML;
};
windmill.registry.methods['asserts.assertNotText'] = {'locator': true, 'option': 'validator' };

// run setup before every test
(function() {
  var old = windmill.jsTest.getCompleteListOfTestNames;
  windmill.jsTest.getCompleteListOfTestNames = function() {
    old.call(this);
    var tests = this.testList;
    if(tests[0].match(/\.setup/)) {
      var tests_without_setup = [];
      var setup = tests.shift();
      for(var i = 0; i < tests.length; i++) {
        if(!tests[i].match(/\.setup/)) {
          tests_without_setup.push(tests[i]);
        };
      };
      
      var new_tests = [];
      for(var i = 0; i < tests_without_setup.length; i++) {
        new_tests.push(setup);
        new_tests.push(tests_without_setup[i]);
      };
      this.testList = new_tests;
    }
  };
})();