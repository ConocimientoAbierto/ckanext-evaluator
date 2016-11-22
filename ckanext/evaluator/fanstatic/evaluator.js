"use strict";

ckan.module('evaluator_goodtables', function ($, _) {
  return {
    initialize: function () {
      console.log("hola desde ckan", this.el);
      alert('hola');
    }
  };
});
