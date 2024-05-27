# Docker konteyneri için temel alınacak resmi Python görüntüsünün versiyonunu belirtir.
# Burada Python'ın 3.12.2 versiyonu kullanılmaktadır.
FROM python:3.12.2

# Konteyner içindeki çalışma dizinini /app olarak ayarlar.
# Böylece, konteyner içindeki komutlar bu dizinde çalışır.
WORKDIR /app

# Bu komut, Dockerfile'ın bulunduğu dizindeki tüm dosyaları konteynerin /app dizinine kopyalar.
# Bu sayede uygulamanın tüm dosyaları konteynere taşınmış olur.
COPY . ./

# Konteynerin 8081 portunu dış dünya ile paylaşılabilir hale getirir.
# Bu, uygulamanın dışarıdan bu porta erişilebilir olmasını sağlar.
EXPOSE 8081

# Konteyner için bir çevre değişkeni tanımlar. Bu örnekte, NAME adında
# bir değişken World değeri ile tanımlanmıştır.
# Uygulama içinde bu değişkeni kullanarak dinamik veri sağlanabilir.
ENV NAME World

# Konteyner çalıştırıldığında varsayılan olarak app.py adlı Python dosyasını çalıştırır.
# Bu komut, konteyner her başlatıldığında çalıştırılacak komutu belirler.
CMD ["python", "app.py"]
