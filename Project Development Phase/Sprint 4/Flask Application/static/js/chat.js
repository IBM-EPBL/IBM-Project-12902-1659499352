<script>
    window.watsonAssistantChatOptions = {
      integrationID: "525df91b-26c4-421d-8ba9-9756a0c0bae2", // The ID of this integration.
      region: "au-syd", // The region your integration is hosted in.
      serviceInstanceID: "790053fb-fa61-4744-aff5-8f30a8fa399d", // The ID of your service instance.
      onLoad: function(instance) { instance.render(); }
    };
    setTimeout(function(){
      const t=document.createElement('script');
      t.src="https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js";
      document.head.appendChild(t);
    });
  </script>