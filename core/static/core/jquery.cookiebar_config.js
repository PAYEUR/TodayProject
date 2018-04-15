$(document).ready(function(){
 $.cookieBar({
     message: 'En poursuivant la navigation vous acceptez les cookies',
     acceptText: 'OK',
     policyButton: true,
     policyText: 'Conditions',
     policyURL: '{% url 'core:cookies' %}',
  {# dev purpose only #}
     forceShow: false,
     renewOnVisit: false

 });
});