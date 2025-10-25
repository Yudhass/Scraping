1. akses link https://arenhost.id/client/cart.php?a=add&domain=register
2. cek input <form method="post" action="cart.php" id="frmDomainChecker">
<input type="hidden" name="token" value="1bc4c4c3483248327ef832d4f95ffae278d74732">
                        <input type="hidden" name="a" value="checkDomain">
                        <div class="row">
                            <div class="col-md-8 col-md-offset-2 col-xs-10 col-xs-offset-1">
                                <div class="input-group input-group-lg input-group-box">
                                    <input type="text" name="domain" class="form-control" placeholder="Find your new domain name" value="" id="inputDomain" data-toggle="tooltip" data-placement="left" data-trigger="manual" title="" data-original-title="Enter a domain or keyword">
                                    <span class="input-group-btn">
                                        <button type="submit" id="btnCheckAvailability" class="btn btn-primary domain-check-availability">Search</button>
                                    </span>
                                </div>
                            </div>

                                                    </div>
                    </form>
3. isi domain dengan kombinasi 3 huruf yang sama, jika sudah semua kombinasikan 3 huruf yang berbeda dengan berakhiran .top
4. kemudian klik button nya
5. tunggu proses nya dia sampai selesai
6. jika sudah tangkap informasi di sini 
jika ada : <p class="domain-available domain-checker-available">Congratulations! <strong>nnn.top</strong> is available!</p>
jika tidak ada : <p class="domain-unavailable domain-checker-unavailable" style="display: block;"><strong>oo.top</strong> is unavailable</p>
7. catat dia berhasil atau tidak dengan domain nya apa
8. catatan format : nama domain | ada/tidak ada
9. tunggu selama 5 detik untuk mencegah aktifitas bot
10. ulangi sampai semua kombinasi nya habis atau tidak ada lagi kombinasi yang memungkinkan, dalam mengulangi reload halaman kemudian isi kembali input domain nya begitu seterus nya jangan sampai berhenti kecuali ada interupsi dari user

buat menggunakan nodejs pupperter
nama file scrap_arent.js