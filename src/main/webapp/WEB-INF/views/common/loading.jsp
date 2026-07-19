<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>

<div id="global-loading" class="hidden fixed inset-0 z-[9999] flex items-center justify-center bg-black/40">
  <div class="flex flex-col items-center gap-3">
    <div class="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
    <span class="text-white text-sm font-medium">처리 중...</span>
  </div>
</div>
<script>
  function showLoading() { document.getElementById('global-loading').classList.remove('hidden'); }
  function hideLoading() { document.getElementById('global-loading').classList.add('hidden'); }
</script>