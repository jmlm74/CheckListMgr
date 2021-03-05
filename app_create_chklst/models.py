import uuid

from django.db import models
from django.db.models import UniqueConstraint

from app_user.models import User, Company


"""
In these models: 
- all the foreign key on Company model are also used to get a unique constraint
on model - company --> U can't have a duplicate on a company but 2 companies may have the same
line-key or category-key
- All the indexes are on the company  
"""


class Heading(models.Model):
    """
    Heading model
    Headings for lines and categories --> used for filtering
    """

    head_key = models.CharField(max_length=30, verbose_name='head key')

    head_company = models.ForeignKey(Company,
                                     related_name='heading',
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True,
                                     default=None)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Heading'
        verbose_name_plural = 'Headings'
        constraints = [
            UniqueConstraint(fields=['head_key', ], name='Unique heading'),
        ]
        ordering = ['head_key', ]
        indexes = [
            models.Index(fields=['head_key'], name='I_Headings'),
        ]

    def __str__(self):
        return self.head_key


class Line(models.Model):
    """
    Line Model
    may be in several Check-lists --> Check list have a many to many relationship
    """
    class LineType(models.TextChoices):
        CHOICE = "C", "Choice"
        TEXT = "T", "Text"

    line_key = models.CharField(max_length=30, verbose_name='Line key')
    line_wording = models.CharField(max_length=80, verbose_name='Line title')
    line_enable = models.BooleanField(verbose_name='Line enabled', default=True)
    line_type = models.CharField(max_length=1,
                                 verbose_name="Line Type",
                                 choices=LineType.choices,
                                 default=LineType.CHOICE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    line_company = models.ForeignKey(Company, related_name='line', on_delete=models.CASCADE)
    line_heading = models.ForeignKey(Heading,
                                     related_name='line_heading',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Line'
        verbose_name_plural = 'Lines'
        constraints = [
            UniqueConstraint(fields=['line_key', 'line_company'], name='Unique line/society'),
        ]
        ordering = ['line_company', 'line_key']
        indexes = [
            models.Index(fields=['line_company'], name='I_Line_Company'),
        ]

    def __str__(self):
        return self.line_key


class Category(models.Model):
    """
    Category model
    may be in several Check-lists --> Check list have a many to many relationship
    """
    cat_key = models.CharField(max_length=30, verbose_name='Category key')
    cat_wording = models.CharField(max_length=80, verbose_name='Category title')
    cat_enable = models.BooleanField(verbose_name='Category enabled', default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    cat_company = models.ForeignKey(Company, related_name='category', on_delete=models.CASCADE, blank=True)
    cat_heading = models.ForeignKey(Heading,
                                     related_name='cat_heading',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        constraints = [
            UniqueConstraint(fields=['cat_key', 'cat_company'], name='Unique category/society'),
        ]
        ordering = ['cat_company', 'cat_key']
        indexes = [
            models.Index(fields=['cat_company'], name='I_Cat_Company'),
        ]

    def __str__(self):
        return self.cat_key


class CheckList(models.Model):
    """
    Checklist model
    A check list may have several categories and several lines (The "through" is to give the
        position in the Checklist)
    The checklist  of course have a company and a user (not used here but may be later for stats)

    The method chklst_detail returns the complete detail for the instance
    --> The categories & lines in the proper order to be displayed
    """
    chk_key = models.CharField(max_length=30, verbose_name='Check-List key')
    chk_title = models.CharField(max_length=80, verbose_name='Check-List title')
    chk_enable = models.BooleanField(verbose_name='Check-List enabled')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    chk_company = models.ForeignKey(Company, related_name='ckecklist', on_delete=models.CASCADE)
    chk_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    chk_category = models.ManyToManyField(Category,
                                          through='CheckListCategory',
                                          related_name='checklist',
                                          blank=True,
                                          default=None,
                                          symmetrical=False)
    chk_line = models.ManyToManyField(Line,
                                      through='CheckListLine',
                                      related_name='checklist',
                                      blank=True,
                                      default=None,
                                      symmetrical=False)

    class Meta:
        verbose_name = 'Check-List'
        verbose_name_plural = 'Check-Lists'
        UniqueConstraint(fields=['chk_key', 'chk_company'], name='Unique checklist/society')
        ordering = ['chk_company', 'chk_key']
        indexes = [
            models.Index(fields=['chk_company'], name='I_Chk_Company')
        ]

    def __str__(self):
        return self.chk_key

    def chklst_detail(self):
        liste = []
        lines = self.chk_line.all()
        for line in lines:
            mydict = {'line_cat': 'line',
                      'pos': line.cll_lines.get(chk_line_checklist_id=self.id).chk_line_position,
                      'key': line.line_key,
                      'wording': line.line_wording,
                      'id': line.id,
                      'type': line.line_type}
            liste.append(mydict)

        categories = self.chk_category.all()
        for category in categories:
            mydict = {'line_cat': 'cat',
                      'pos': category.clc_categories.get(chk_cat_checklist_id=self.id).chk_cat_position,
                      'key': category.cat_key,
                      'wording': category.cat_wording,
                      'id': category.id,
                      'type': None}
            liste.append(mydict)

        liste2 = sorted(liste, key=lambda mydic: mydic['pos'])
        return liste2

    def delete(self):
        """
        Don't delete a checklist and Don't change id --> link with checklistdone !
        set company to dummy company (visible only by site admin)
        rename key with uuid to avoid duplicate (same company !)
        """
        company = Company.objects.get(pk=1000000)
        self.chk_company = company
        self.chk_key = self.chk_key[0:20] + "-" + str(uuid.uuid4().hex)[:8]
        self.save()
        return True


class CheckListCategory(models.Model):
    """
       Many to many relationship between CheckList & categories with the position
       The unique constraint is to prevent having a category twice in a checklist.
       It should be not possible but .... :)
    """
    chk_cat_position = models.PositiveSmallIntegerField(verbose_name='Category Position')
    chk_cat_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='clc_categories')
    chk_cat_checklist = models.ForeignKey(CheckList, on_delete=models.CASCADE, related_name='clc_checklists')

    class Meta:
        UniqueConstraint(fields=['chk_cat_category', 'chk_cat_checklist'], name='Unique checklistcategory')
        ordering = ['chk_cat_checklist', ]
        indexes = [
            models.Index(fields=['chk_cat_checklist'], name='I_CheckListCategory')
        ]

    def __str__(self):
        return str(self.chk_cat_position)


class CheckListLine(models.Model):
    """
    Many to many relationship between CheckList & Lines with the position
    The unique constraint is to prevent having a line twice in a checklist.
    It should be not possible but .... :)
    """
    chk_line_position = models.PositiveSmallIntegerField(verbose_name='Line Position')
    chk_line_line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name='cll_lines')
    chk_line_checklist = models.ForeignKey(CheckList, on_delete=models.CASCADE, related_name='cll_checklists')

    class Meta:
        UniqueConstraint(fields=['chk_line_line', 'chk_line_checklist'], name='Unique checklistline')
        ordering = ['chk_line_checklist', ]
        indexes = [
            models.Index(fields=['chk_line_checklist'], name='I_CheckListLine')
        ]

    def __str__(self):
        return str(self.chk_line_position)
