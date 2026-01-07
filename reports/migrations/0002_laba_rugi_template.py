from django.db import migrations


def create_laba_rugi_template(apps, schema_editor):
    ReportTemplate = apps.get_model("reports", "ReportTemplate")
    TemplateItem = apps.get_model("reports", "TemplateItem")

    template, _ = ReportTemplate.objects.get_or_create(
        slug="laba-rugi",
        defaults={
            "name": "Laporan Laba Rugi dan Penghasilan Komprehensif Lain",
            "description": "Template laba rugi dan penghasilan komprehensif lain.",
        },
    )

    items = [
        (
            "Laporan laba rugi dan penghasilan komprehensif lain",
            "Statementofprofitorlossandothercomprehensiveincome",
        ),
        ("Penjualan dan pendapatan usaha", "Salesandrevenue"),
        ("Beban pokok penjualan dan pendapatan", "Costofsalesandrevenue"),
        ("Jumlah laba bruto", "Totalgrossprofit"),
        ("Beban penjualan", "Sellingexpenses"),
        ("Beban umum dan administrasi", "Generalandadministrativeexpenses"),
        ("Pendapatan dividen", "Dividendsincome"),
        ("Pendapatan bunga", "Interestincome"),
        ("Pendapatan investasi", "Investmentincome"),
        ("Pendapatan keuangan", "Financeincome"),
        ("Beban bunga dan keuangan", "Interestandfinancecosts"),
        (
            "Keuntungan (kerugian) selisih kurs mata uang asing",
            "Gains(losses)onchangesinforeignexchangerates",
        ),
        (
            "Bagian atas laba (rugi) entitas asosiasi yang dicatat dengan menggunakan metode ekuitas",
            "Shareofprofit(loss)ofassociatesaccountedforusingequitymethod",
        ),
        (
            "Bagian atas laba (rugi) entitas ventura bersama yang dicatat menggunakan metode ekuitas",
            "Shareofprofit(loss)ofjointventuresaccountedforusingequitymethod",
        ),
        (
            "Keuntungan (kerugian) perubahan nilai wajar efek",
            "Gains(losses)onchangesinfairvalueofmarketablesecurities",
        ),
        (
            "Keuntungan (kerugian) dari transaksi perdagangan efek yang telah direalisasi",
            "Realisedgains(losses)ontradingofmarketablesecurities",
        ),
        (
            "Keuntungan (kerugian) atas instrumen keuangan derivatif",
            "Gains(losses)onderivativefinancialinstruments",
        ),
        ("Beban pajak final", "Finaltaxexpenses"),
        ("Pendapatan lainnya", "Otherincome"),
        ("Beban lainnya", "Otherexpenses"),
        ("Keuntungan (kerugian) lainnya", "Othergains(losses)"),
        ("Jumlah laba (rugi) sebelum pajak penghasilan", "Totalprofit(loss)beforetax"),
        ("Pendapatan (beban) pajak", "Taxbenefit(expenses)"),
        (
            "Jumlah laba (rugi) dari operasi yang dilanjutkan",
            "Totalprofit(loss)fromcontinuingoperations",
        ),
        (
            "Laba (rugi) dari operasi yang dihentikan",
            "Profit(loss)fromdiscontinuedoperations",
        ),
        ("Jumlah laba (rugi)", "Totalprofit(loss)"),
        ("Pendapatan komprehensif lainnya, sebelum pajak", "Othercomprehensiveincome,beforetax"),
        (
            "Pendapatan komprehensif lainnya yang tidak akan direklasifikasi ke laba rugi, sebelum pajak",
            "Othercomprehensiveincomethatwillnotbereclassifiedtoprofitorloss,beforetax",
        ),
        (
            "Pendapatan komprehensif lainnya atas keuntungan (kerugian) hasil revaluasi aset tetap, sebelum pajak",
            "Othercomprehensiveincomeforgains(losses)onrevaluationofproperty,plantandequipment,beforetax",
        ),
        (
            "Pendapatan komprehensif lainnya atas pengukuran kembali kewajiban manfaat pasti, sebelum pajak",
            "Othercomprehensiveincomeforremeasurementofdefinedbenefitobligation,beforetax",
        ),
        (
            "Penyesuaian lainnya atas pendapatan komprehensif lainnya yang tidak akan direklasifikasi ke laba rugi, sebelum pajak",
            "Otheradjustmentstoothercomprehensiveincomethatwillnotbereclassifiedtoprofitorloss,beforetax",
        ),
        (
            "Jumlah pendapatan komprehensif lainnya yang tidak akan direklasifikasi ke laba rugi, sebelum pajak",
            "Totalothercomprehensiveincomethatwillnotbereclassifiedtoprofitorloss,beforetax",
        ),
        (
            "Pendapatan komprehensif lainnya yang akan direklasifikasi ke laba rugi, sebelum pajak",
            "Othercomprehensiveincomethatmaybereclassifiedtoprofitorloss,beforetax",
        ),
        (
            "Keuntungan (kerugian) selisih kurs penjabaran, sebelum pajak",
            "Gains(losses)onexchangedifferencesontranslation,beforetax",
        ),
        (
            "Penyesuaian reklasifikasi selisih kurs penjabaran, sebelum pajak",
            "Reclassificationadjustmentsonexchangedifferencesontranslation,beforetax",
        ),
        (
            "Keuntungan (kerugian) yang belum direalisasi atas perubahan nilai wajar aset keuangan melalui penghasilan komprehensif lain, sebelum pajak",
            "Unrealisedgains(losses)onchangesinfairvaluethroughothercomprehensiveincome,beforetax",
        ),
        (
            "Penyesuaian reklasifikasi atas aset keuangan nilai wajar melalui pendapatan komprehensif lainnya, sebelum pajak",
            "Reclassificationadjustmentsonfairvaluethroughothercomprehensiveincomefinancialassets,beforetax",
        ),
        (
            "Keuntungan (kerugian) lindung nilai arus kas, sebelum pajak",
            "Gains(losses)oncashflowhedges,beforetax",
        ),
        (
            "Penyesuaian reklasifikasi atas lindung nilai arus kas, sebelum pajak",
            "Reclassificationadjustmentsoncashflowhedges,beforetax",
        ),
        (
            "Nilai tercatat dari aset (liabilitas) non-keuangan yang perolehan atau keterjadiannya merupakan suatu prakiraan transaksi yang kemungkinan besar terjadi yang dilindung nilai, sebelum pajak",
            "Carryingamountofnon-financialasset(liability)whoseacquisitionorincurrencewashedgedonhighlyprobableforecasttransaction,adjustedfromequity,beforetax",
        ),
        (
            "Keuntungan (kerugian) lindung nilai investasi bersih kegiatan usaha luar negeri, sebelum pajak",
            "Gains(losses)onhedgesofnetinvestmentsinforeignoperations,beforetax",
        ),
        (
            "Penyesuaian reklasifikasi atas lindung nilai investasi bersih kegiatan usaha luar negeri, sebelum pajak",
            "Reclassificationadjustmentsonhedgesofnetinvestmentsinforeignoperations,beforetax",
        ),
        (
            "Bagian pendapatan komprehensif lainnya dari entitas asosiasi yang dicatat dengan menggunakan metode ekuitas, sebelum pajak",
            "Shareofothercomprehensiveincomeofassociatesaccountedforusingequitymethod,beforetax",
        ),
        (
            "Bagian pendapatan komprehensif lainnya dari entitas ventura bersama yang dicatat dengan menggunakan metode ekuitas, sebelum pajak",
            "Shareofothercomprehensiveincomeofjointventuresaccountedforusingequitymethod,beforetax",
        ),
        (
            "Penyesuaian lainnya atas pendapatan komprehensif lainnya yang akan direklasifikasi ke laba rugi, sebelum pajak",
            "Otheradjustmentstoothercomprehensiveincomethatmaybereclassifiedtoprofitorloss,beforetax",
        ),
        (
            "Jumlah pendapatan komprehensif lainnya yang akan direklasifikasi ke laba rugi, sebelum pajak",
            "Totalothercomprehensiveincomethatmaybereclassifiedtoprofitorloss,beforetax",
        ),
        ("Jumlah pendapatan komprehensif lainnya, sebelum pajak", "Totalothercomprehensiveincome,beforetax"),
        ("Pajak atas pendapatan komprehensif lainnya", "Taxonothercomprehensiveincome"),
        ("Jumlah pendapatan komprehensif lainnya, setelah pajak", "Totalothercomprehensiveincome,aftertax"),
        ("Jumlah laba rugi komprehensif", "Totalcomprehensiveincome"),
        ("Laba (rugi) yang dapat diatribusikan", "Profit(loss)attributableto"),
        ("Laba (rugi) yang dapat diatribusikan ke entitas induk", "Profit(loss)attributabletoparententity"),
        (
            "Laba (rugi) yang dapat diatribusikan ke kepentingan non-pengendali",
            "Profit(loss)attributabletonon-controllinginterests",
        ),
        ("Laba rugi komprehensif yang dapat diatribusikan", "Comprehensiveincomeattributableto"),
        (
            "Laba rugi komprehensif yang dapat diatribusikan ke entitas induk",
            "Comprehensiveincomeattributabletoparententity",
        ),
        (
            "Laba rugi komprehensif yang dapat diatribusikan ke kepentingan non-pengendali",
            "Comprehensiveincomeattributabletonon-controllinginterests",
        ),
        ("Laba (rugi) per saham", "Earnings(loss)pershare"),
        (
            "Laba per saham dasar diatribusikan kepada pemilik entitas induk",
            "Basicearningspershareattributabletoequityownersoftheparententity",
        ),
        (
            "Laba (rugi) per saham dasar dari operasi yang dilanjutkan",
            "Basicearnings(loss)persharefromcontinuingoperations",
        ),
        (
            "Laba (rugi) per saham dasar dari operasi yang dihentikan",
            "Basicearnings(loss)persharefromdiscontinuedoperations",
        ),
        ("Laba (rugi) per saham dilusian", "Dilutedearnings(loss)pershare"),
        (
            "Laba (rugi) per saham dilusian dari operasi yang dilanjutkan",
            "Dilutedearnings(loss)persharefromcontinuingoperations",
        ),
        (
            "Laba (rugi) per saham dilusian dari operasi yang dihentikan",
            "Dilutedearnings(loss)persharefromdiscontinuedoperations",
        ),
    ]

    for order, (label, primary_fact) in enumerate(items, start=1):
        item, created = TemplateItem.objects.get_or_create(
            template=template,
            label=label,
            defaults={"primary_fact": primary_fact, "order": order},
        )
        if not created:
            updates = {}
            if item.primary_fact != primary_fact:
                updates["primary_fact"] = primary_fact
            if item.order != order:
                updates["order"] = order
            if updates:
                TemplateItem.objects.filter(pk=item.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_laba_rugi_template, migrations.RunPython.noop),
    ]
