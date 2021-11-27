;;Загружаем библиотеку квик лисп для других либ
sbcl --load quicklisp.lisp



;;Загружаем сл-цсв для работы цсв файламис 
(ql:quickload "cl-csv")
;; подгружаем данные
(defparameter input (cl-csv:read-csv #P"out.csv"))

;; Делаем инит переменной-параметра очков
(defparameter score ())
;; Переводим очки, записаные в строке, в число
(loop for line in input
   do (push (nth 0 (with-input-from-string (in (nth 1 line))
  (loop for x = (read in nil nil) while x collect x))) score))

;;аналогично для времени
(defparameter times ())
(loop for line in input
   do (push (nth 0 (with-input-from-string (in (nth 2 line))
  (loop for x = (read in nil nil) while x collect x))) times))
;; считаем среднее для времени М(Х)
(defparameter mean_time 0)
(setq mean_time (/ (apply '+ times) (length times)))
;; считаем среднее для очков М(Х)
(defparameter mean_score 0)
(setq mean_score (/ (apply '+ score) (float (length score))))
;; считаем дисперсию для очков, по извесной формуле применяэ функицю мапкар, которая по очередно к массиву применяет заданую
;;функцию в первом аргументе, тут видно, что мы юзаем ее два раза, первый для просчета отклонений, потом для 
;;возведении его в квадрат, в конце делим на кол-во елементов
(defparameter variance_score 0)
(setq variance_score (/ (apply '+ (mapcar (lambda (x) (* x x)) (mapcar (lambda (n) (- n mean_score))
        score))) (length score)))
;;тут выводим все
mean_time
variance_score
