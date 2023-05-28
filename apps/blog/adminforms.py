from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dal import autocomplete
from django import forms

from .models import Category, Tag, Post


class PostAdminForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=autocomplete.ModelSelect2(url="category-autocomplete"),
        label="分类",
    )
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'),
        label='标签',
    )

    desc = forms.CharField(widget=forms.Textarea(), label="摘要", required=False)
    # 可以上传图片
    # django-ckeditor
    content_ck = forms.CharField(widget=CKEditorUploadingWidget(), label="正文(ckeditor)", required=False)
    # markdown
    content_md = forms.CharField(widget=forms.Textarea(), label="正文(markdown)", required=False)
    # HiddenInput，用来接受最终的content
    content = forms.CharField(widget=forms.HiddenInput(), label="正文", required=False)

    class Meta:
        model = Post
        fields = (
            # 自动补全的字段放在前面
            "category",
            "tag",
            "title",
            "desc",
            "content_ck",
            "content_md",
            "content",
            "status",
        )

    def __init__(self, instance=None, initial=None, **kwargs):
        # initial 是form中各字段的初始化值
        # instance 是当前对象的实例，比如编辑一篇文章，就是当前文章的实例。
        initial = initial or {}
        if instance:
            if instance.is_md:
                initial["content_md"] = instance.content
            else:
                initial["content_ck"] = instance.content

        super(PostAdminForm, self).__init__(instance=instance, initial=initial, **kwargs)

    def clean(self):
        is_md = self.cleaned_data.get("is_md")
        # 判断是否使用了Markdown语法
        if is_md:
            content_field_name = "content_md"
        else:
            content_field_name = "content_ck"
        # 最终赋值给content
        content = self.cleaned_data.get(content_field_name)

        if not content:
            self.add_error(content_field_name, "必填项！")
            return
        self.cleaned_data["content"] = content

        return super(PostAdminForm, self).clean()

    class Media:
        js =("js/post_editor.js",)
