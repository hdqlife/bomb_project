def ver_data(request):

    resp = {}
    rev_data = VersionTable.objects.values()
    resp['ver'] = list(rev_data)
    respond_data = User.objects.values()
    resp['data'] = list(respond_data)
    # return HttpResponse(json.dumps(result), content_type="application/json")
    return JsonResponse(resp, safe=False)