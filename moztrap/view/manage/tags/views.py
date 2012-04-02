"""
Manage views for tags.

"""
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from cc import model

from cc.view.filters import TagFilterSet
from cc.view.lists import decorators as lists
from cc.view.users.decorators import permission_required
from cc.view.utils.ajax import ajax
from cc.view.utils.auth import login_maybe_required

from ..finders import ManageFinder

from . import forms



@never_cache
@login_maybe_required
@lists.actions(
    model.Tag,
    ["delete", "clone"],
    permission="tags.manage_tags")
@lists.finder(ManageFinder)
@lists.filter("tags", filterset_class=TagFilterSet)
@lists.sort("tags")
@ajax("manage/tag/list/_tags_list.html")
def tags_list(request):
    """List tags."""
    return TemplateResponse(
        request,
        "manage/tag/tags.html",
        {
            "tags": model.Tag.objects.all(),
            }
        )



@never_cache
@permission_required("tags.manage_tags")
def tag_add(request):
    """Add a tag."""
    if request.method == "POST":
        form = forms.AddTagForm(request.POST, user=request.user)
        tag = form.save_if_valid()
        if tag is not None:
            messages.success(
                request, "Tag '{0}' added.".format(
                    tag.name)
                )
            return redirect("manage_tags")
    else:
        form = forms.AddTagForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/tag/add_tag.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("tags.manage_tags")
def tag_edit(request, tag_id):
    """Edit a tag."""
    tag = get_object_or_404(model.Tag, pk=tag_id)
    if request.method == "POST":
        form = forms.EditTagForm(
            request.POST, instance=tag, user=request.user)
        saved_tag = form.save_if_valid()
        if saved_tag is not None:
            messages.success(request, "Saved '{0}'.".format(saved_tag.name))
            return redirect("manage_tags")
    else:
        form = forms.EditTagForm(instance=tag, user=request.user)
    return TemplateResponse(
        request,
        "manage/tag/edit_tag.html",
        {
            "form": form,
            "tag": tag,
            }
        )



@never_cache
@login_maybe_required
def tag_autocomplete(request):
    """Return autocomplete list of existing tags in JSON format."""
    text = request.GET.get("text")
    product_id = request.GET.get("product-id")
    if text is not None:
        tags = model.Tag.objects.filter(name__icontains=text)
        if product_id is not None:
            tags = tags.filter(Q(product=product_id) | Q(product=None))
    else:
        tags = []
    suggestions = []
    for tag in tags:
        # can't just use split due to case; we match "text" insensitively, but
        # want pre and post to be case-accurate
        start = tag.name.lower().index(text.lower())
        pre = tag.name[:start]
        post = tag.name[start+len(text):]
        suggestions.append({
                "preText": pre,
                "typedText": text,
                "postText": post,
                "id": tag.id,
                "product-id": tag.product.id if tag.product else None,
                "name": tag.name,
                "type": "tag",
                })
    return HttpResponse(
        json.dumps(
            {
                "suggestions": suggestions
                }
            ),
        content_type="application/json",
        )