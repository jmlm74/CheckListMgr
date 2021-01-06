from app_checklist.models import CheckListDone

# shell_plus
# from app_utilities.migration_title_210106 import go
# go()

def go():
    ckds = CheckListDone.objects.filter(cld_title="XXX")
    for ckd in ckds:
        ckd.cld_title
        ckd.cld_checklist.chk_title
        ckd.cld_title = ckd.cld_checklist.chk_title
        ckd.save()


if __name__ == '__main__':
    go()
